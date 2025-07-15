from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import FunctionTool, google_search, ToolContext
from .prompt import create_design_agent_instruction
from .tools import (
    # 新しいToolContext対応ツール
    get_vue_component_from_artifacts,
    list_vue_components_in_artifacts,
    # 新しいVueファイル管理ツール
    save_vue_file_to_artifact,
    save_all_vue_files_to_artifacts,
    # 既存のツール
    create_ui_design, 
    get_project_info
)

# CallbackContext type for hints (optional)
from typing import Optional
from google.adk.agents.callback_context import CallbackContext

# 環境変数を読み込み
load_dotenv()


# ---------------------------------------------
# before_agent_callback: preload Vue artifacts
# ---------------------------------------------

async def _preload_vue(callback_context: CallbackContext) -> Optional[None]:
    """Save all project Vue files to Artifact once per session.

    Runs *before* design_agent executes. Uses the session state flag
    `_vue_artifacts_loaded` to ensure the batch save runs only once per session.
    """

    if callback_context.state.get("_vue_artifacts_loaded"):
        return None

    # Convert CallbackContext -> ToolContext so that tool functions work
    tool_ctx = ToolContext(
        invocation_context=callback_context._invocation_context,  # type: ignore[attr-defined]
        event_actions=callback_context._event_actions,  # type: ignore[attr-defined]
    )

    await save_all_vue_files_to_artifacts(tool_ctx)
    callback_context.state["_vue_artifacts_loaded"] = True
    return None

def create_design_agent():
    """Design Agentを作成"""
    
    # ツールを作成
    tools = [
        # Google検索ツール（最重要）
        google_search,
        
        # 新しいToolContext対応のArtifactツール
        FunctionTool(func=get_vue_component_from_artifacts),
        FunctionTool(func=list_vue_components_in_artifacts),
        
        # 新しいVueファイル管理ツール
        FunctionTool(func=save_vue_file_to_artifact),
        FunctionTool(func=save_all_vue_files_to_artifacts),
        
        # 基本的なUI設計ツール
        FunctionTool(func=create_ui_design),
        
        # 基本情報取得ツール
        FunctionTool(func=get_project_info),
    ]
    
    # エージェントを作成
    agent = Agent(
        name="design_agent",
        model="gemini-1.5-flash-8b",
        description="最新のMaterial Design 3とVuetify 3情報を検索し、既存コンポーネントを参照して、Vue.jsコンポーネントを生成します",
        instruction=create_design_agent_instruction(),
        tools=tools,
        before_agent_callback=_preload_vue,
    )
    
    return agent 