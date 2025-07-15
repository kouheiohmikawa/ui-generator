"""
Design Agent のツール関数（ToolContext対応版）
"""

import os
import glob
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from google.adk.tools import ToolContext
from google.genai.types import Part

logger = logging.getLogger(__name__)

# ------------------------------
# Artifact Lazy-Load Helper
# ------------------------------
_vue_artifacts_loaded_key = "_vue_artifacts_loaded"  # Session state flag


async def _ensure_vue_artifacts(tool_context: ToolContext) -> None:
    """Ensure Vue files are present in Artifact service for current session.

    If no artifact exists yet, this helper runs `save_all_vue_files_to_artifacts` once
    per session. Subsequent calls are skipped using a flag stored in session state.
    """
    try:
        # Skip when already loaded in this session
        if tool_context.state.get(_vue_artifacts_loaded_key):
            return

        # Check existing artifacts; run batch save only if empty
        existing = await tool_context.list_artifacts()
        if not existing:
            await save_all_vue_files_to_artifacts(tool_context)

        # Mark as loaded to avoid duplicate work
        tool_context.state[_vue_artifacts_loaded_key] = True
    except Exception as e:
        # Log and continue – downstream functions will surface errors if needed
        logger.warning("_ensure_vue_artifacts skipped due to error: %s", e)

# 新しいVueファイル管理ツール
async def save_vue_file_to_artifact(
    tool_context: ToolContext,
    vue_file_path: str,
    output_filename: Optional[str] = None
) -> str:
    """指定されたVueファイルをそのままArtifactに保存する

    Args:
        tool_context: ToolContext
        vue_file_path: 保存する .vue ファイルのパス（絶対またはプロジェクトルートからの相対パス）
        output_filename: Artifact 上のファイル名（省略時は vue/ 以下に同じ相対パスで保存）

    Returns:
        成功時: 成功メッセージ
        失敗時: エラーメッセージ
    """
    try:
        # 渡されたパスをそのまま使用（検索は行わない）
        file_path = Path(vue_file_path)

        # 相対パスの場合はプロジェクトルートからの相対として扱う
        if not file_path.is_absolute():
            current_dir = Path(__file__).resolve()
            project_root = current_dir.parents[4]
            file_path = (project_root / file_path).resolve()

        if not file_path.exists():
            return f"❌ File not found: {file_path}"

        # ファイル内容を読み込み
        vue_content = file_path.read_text(encoding="utf-8")

        # 出力ファイル名を決定
        if output_filename is None:
            # プロジェクトルートからの相対パスをそのままArtifact名にする
            current_dir = Path(__file__).resolve()
            project_root = current_dir.parents[4]
            rel_path = file_path.relative_to(project_root)
            # `user:` 名前空間を付けることで、親エージェントからも閲覧可能にする
            output_filename = f"user:vue/{rel_path}".replace("\\", "/")

        # Artifactに保存
        artifact = Part(text=vue_content)
        await tool_context.save_artifact(filename=output_filename, artifact=artifact)

        logger.info("✅ Saved %s to artifact", output_filename)
        return f"✅ Successfully saved {file_path} to artifact as {output_filename}"

    except Exception as e:
        error_msg = f"❌ Error saving {vue_file_path}: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def save_all_vue_files_to_artifacts(tool_context: ToolContext) -> str:
    """全てのVueファイルをArtifactに一括保存する
    
    Args:
        tool_context: ToolContext
    
    Returns:
        保存結果の詳細レポート
    """
    try:
        # プロジェクトのルートディレクトリを特定
        current_dir = Path(__file__).resolve()
        project_root = current_dir.parents[4]  # 4つ上のディレクトリがプロジェクトルート
        vue_dir = project_root / "src"
        
        if not vue_dir.exists():
            return f"❌ Vue directory not found: {vue_dir}"

        vue_files = list(vue_dir.rglob("*.vue"))
        if not vue_files:
            return f"❌ No Vue files found in: {vue_dir}"

        # 並列で保存処理を実行
        tasks = []
        for vue_file in vue_files:
            rel_path = vue_file.relative_to(project_root)
            tasks.append(save_vue_file_to_artifact(tool_context, str(rel_path)))
        
        results = await asyncio.gather(*tasks)
        
        # 結果を集計
        success_count = sum(1 for r in results if r.startswith("✅"))
        failure_count = len(results) - success_count
        
        report = f"""
        ## Vue ファイル一括保存結果

        **処理結果:**
        - ✅ 成功: {success_count} ファイル
        - ❌ 失敗: {failure_count} ファイル
        - 📁 合計: {len(vue_files)} ファイル

        **詳細:**
        {chr(10).join(results)}
        """
        
        logger.info("Batch save completed: %d success, %d failure", success_count, failure_count)
        return report
        
    except Exception as e:
        error_msg = f"❌ Error during batch save: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def get_vue_component_from_artifacts(tool_context: ToolContext, component_name: str) -> str:
    """
    ArtifactからVueコンポーネントの内容を取得する
    """
    try:
        # component_nameからファイル名を推測
        if not component_name.endswith('.vue'):
            component_name += '.vue'
        
        # 可能性のあるパスを試す
        possible_paths = [
            f"user:vue/{component_name}",
            f"user:vue/components/{component_name}",
            f"user:vue/views/{component_name}",
            f"user:vue/pages/{component_name}",
            # 後方互換（名前空間なし）
            f"vue/{component_name}",
            f"vue/components/{component_name}"
        ]
        
        for filename in possible_paths:
            try:
                artifact = await tool_context.load_artifact(filename)
                if artifact and hasattr(artifact, 'text'):
                    return f"## {component_name}\n\n```vue\n{artifact.text}\n```"
            except Exception:
                continue
        
        return f"❌ Component '{component_name}' not found in artifacts. Available components can be listed with list_vue_components_in_artifacts."
        
    except Exception as e:
        return f"❌ Error retrieving component: {str(e)}"

async def list_vue_components_in_artifacts(tool_context: ToolContext) -> str:
    """Artifact 内の Vue コンポーネント一覧を返す。

    初回呼び出し時に未登録であれば自動で一括登録を行う。
    """
    try:
        # Artifactサービスからキー一覧を取得し、vue/* を抽出
        await _ensure_vue_artifacts(tool_context)
        keys = await tool_context.list_artifacts()
        vue_keys = [k for k in keys if k.startswith("user:vue/") and k.endswith(".vue")]

        if vue_keys:
            component_list = "\n".join(f"- {k.removeprefix('user:')}" for k in vue_keys)
            return (
                "## 登録済みVueコンポーネント\n\n"
                f"{component_list}\n\n"
                "💡 `get_vue_component_from_artifacts(component_name)` で内容を確認できます。"
            )
        return "❌ No Vue components found in artifacts."
    except Exception as e:
        return f"❌ Error listing components: {str(e)}"

def create_ui_design(design_requirements: str) -> str:
    """
    UI設計の基本的なガイダンスを提供
    """
    return f"""## UI設計提案
    
**要件**: {design_requirements}

**推奨アプローチ**:
1. Vue.js 3 + Vuetify 3を使用
2. Material Design 3の原則に従う
3. レスポンシブデザインを実装
4. アクセシビリティを考慮

**次のステップ**:
- 既存コンポーネントを確認: `list_vue_components_in_artifacts()`
- 具体的なコンポーネントの詳細を取得: `get_vue_component_from_artifacts(component_name)`
- Material Design 3の最新情報を検索
"""

def get_project_info() -> str:
    """
    プロジェクトの基本情報を取得
    """
    return """## プロジェクト情報

**技術スタック**:
- Vue.js 3 (Composition API)
- Vuetify 3 (Material Design 3)
- Vite (ビルドツール)

**構成**:
- `src/`: Vueアプリケーションのソースコード
- `src/components/`: 再利用可能なコンポーネント
- `src/assets/`: 静的アセット

**開発方針**:
- Material Design 3のガイドラインに準拠
- レスポンシブデザイン
- アクセシビリティ対応
- モダンなUI/UX
"""

# """
# Design Agent のツール関数（Artifact準備版）
# """

# import os
# import glob
# from typing import List, Dict, Any

# def get_existing_components_summary() -> str:
#     """
#     既存のVueコンポーネントの概要を取得
    
#     Returns:
#         既存コンポーネントのサマリー
#     """
    
#     # Vueファイルを探す
#     vue_files = []
#     patterns = [
#         '../../src/*.vue',
#         '../../src/components/*.vue',
#         '../../src/views/*.vue',
#         '../../src/pages/*.vue'
#     ]
    
#     for pattern in patterns:
#         vue_files.extend(glob.glob(pattern))
    
#     if not vue_files:
#         return "既存のVueファイルが見つかりませんでした。"
    
#     summary = f"## 既存コンポーネント（{len(vue_files)}個）\n\n"
#     summary += "以下の既存コンポーネントが利用可能です：\n\n"
    
#     for file_path in vue_files:
#         if os.path.exists(file_path):
#             component_name = os.path.basename(file_path)
#             file_size = os.path.getsize(file_path)
#             summary += f"- **{component_name}** (`{file_path}`, {file_size} bytes)\n"
    
#     summary += "\n**使用方法:**\n"
#     summary += "これらのコンポーネントの詳細を確認する場合は、`get_component_details`ツールを使用してください。\n"
#     summary += "大容量ファイルも完全に読み込まれ、パターン参照に使用できます。\n"
#     summary += "\n**注意:** 今後のバージョンでADK Artifactを使用した高速読み込みに対応予定です。\n"
    
#     return summary

# def get_component_details(component_name: str) -> str:
#     """
#     特定のコンポーネントの詳細を取得
    
#     Args:
#         component_name: コンポーネント名（例：SignUp.vue）
        
#     Returns:
#         コンポーネントの詳細情報
#     """
    
#     # Vueファイルを探す
#     vue_files = []
#     patterns = [
#         '../../src/*.vue',
#         '../../src/components/*.vue',
#         '../../src/views/*.vue',
#         '../../src/pages/*.vue'
#     ]
    
#     for pattern in patterns:
#         vue_files.extend(glob.glob(pattern))
    
#     # 指定されたコンポーネントを検索
#     matching_file = None
#     for file_path in vue_files:
#         if os.path.basename(file_path) == component_name:
#             matching_file = file_path
#             break
    
#     if not matching_file:
#         available_components = [os.path.basename(f) for f in vue_files]
#         return f"コンポーネント '{component_name}' が見つかりません。\n\n利用可能なコンポーネント:\n" + \
#                "\n".join([f"- {comp}" for comp in available_components])
    
#     try:
#         with open(matching_file, 'r', encoding='utf-8') as f:
#             code = f.read()
            
#         result = f"## {component_name} の詳細\n\n"
#         result += f"**ファイルパス:** {matching_file}\n"
#         result += f"**サイズ:** {len(code)} 文字\n\n"
#         result += "**完全なコード:**\n"
#         result += f"```vue\n{code}\n```\n\n"
#         result += "このコンポーネントのパターンを参考にして、統一感のあるデザインを作成してください。\n"
#         result += "特に以下の点を参考にしてください：\n"
#         result += "- Vuetifyコンポーネントの使用方法\n"
#         result += "- レイアウト構造\n"
#         result += "- コードの記述スタイル\n"
#         result += "- カラーパレットとテーマの使用\n"
#         result += "- レスポンシブデザインの実装方法\n"
        
#         return result
        
#     except Exception as e:
#         return f"エラー: {component_name} の読み込みに失敗しました - {str(e)}"

# def create_ui_design(requirement_data: dict) -> dict:
#     """UI設計を作成する"""
    
#     return {
#         "status": "success",
#         "message": "UI設計を作成しました。google_searchツールで最新情報を検索してから詳細な実装を行ってください。",
#         "design_result": {
#             "components": ["Header", "LoginForm", "Footer"],
#             "color_scheme": "Material Design 3 primary colors",
#             "typography": "Material Design 3 typography",
#             "accessibility": "WCAG 2.1 AA準拠",
#             "responsive": "Mobile-first approach"
#         }
#     }

# def get_project_info() -> dict:
#     """
#     プロジェクトの基本情報を取得
    
#     Returns:
#         プロジェクトの基本情報
#     """
#     return {
#         "framework": "Vue.js 3 + Vuetify 3",
#         "design_system": "Material Design 3",
#         "accessibility": "WCAG 2.1 AA準拠",
#         "storage_method": "直接ファイル読み込み（ADK Artifact準備中）",
#         "artifact_status": "今後のバージョンでADK Artifactを使用した高速読み込みに対応予定",
#         "note": "既存コンポーネントは直接読み込まれ、統一されたパターンで管理されています"
#     }
