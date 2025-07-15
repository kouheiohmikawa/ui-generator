from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import FunctionTool
from typing import Dict, List, Any
import json
import re
from .prompt import create_evaluation_instruction
from ...tools.ui_analysis_tools import analyze_vue_component

# 環境変数を読み込み
load_dotenv()

def vue_component_analysis(component_code: str, file_path: str = "component.vue") -> Dict[str, Any]:
    """Vue.jsコンポーネントの詳細分析"""
    try:
        # 一時ファイルに保存して分析
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vue', delete=False) as temp_file:
            temp_file.write(component_code)
            temp_file_path = temp_file.name
        
        try:
            # 既存のanalyze_vue_component関数を使用
            analysis = analyze_vue_component(temp_file_path)
            
            # 追加分析
            additional_analysis = {
                "code_metrics": {
                    "total_lines": len(component_code.split('\n')),
                    "template_complexity": calculate_template_complexity(component_code),
                    "component_structure": analyze_component_structure(component_code)
                },
                "accessibility_issues": detailed_accessibility_check(component_code),
                "performance_indicators": analyze_performance_indicators(component_code)
            }
            
            analysis.update(additional_analysis)
            return analysis
            
        finally:
            # 一時ファイルを削除
            os.unlink(temp_file_path)
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"コンポーネント分析中にエラーが発生: {str(e)}"
        }

def wcag_compliance_check(component_code: str) -> Dict[str, Any]:
    """WCAG 2.1準拠性の詳細チェック"""
    
    compliance_result = {
        "overall_level": "AA",
        "score": 0,
        "max_score": 100,
        "categories": {
            "perceivable": {"score": 0, "max_score": 25, "issues": []},
            "operable": {"score": 0, "max_score": 25, "issues": []},
            "understandable": {"score": 0, "max_score": 25, "issues": []},
            "robust": {"score": 0, "max_score": 25, "issues": []}
        }
    }
    
    # 1. 知覚可能 (Perceivable)
    perceivable_score = 25
    perceivable_issues = []
    
    # 1.1 代替テキスト
    if '<img' in component_code:
        if 'alt=' not in component_code:
            perceivable_issues.append("画像に代替テキストが設定されていません")
            perceivable_score -= 5
    
    # 1.3 色彩のコントラスト
    if 'color:' in component_code:
        perceivable_issues.append("色彩のコントラスト比を確認してください")
        perceivable_score -= 3
    
    # 1.4 フォントサイズ
    if 'font-size:' in component_code:
        font_sizes = re.findall(r'font-size:\s*(\d+)px', component_code)
        small_fonts = [size for size in font_sizes if int(size) < 16]
        if small_fonts:
            perceivable_issues.append(f"16px未満の小さなフォントが使用されています: {small_fonts}")
            perceivable_score -= 5
    
    compliance_result["categories"]["perceivable"]["score"] = perceivable_score
    compliance_result["categories"]["perceivable"]["issues"] = perceivable_issues
    
    # 2. 操作可能 (Operable)
    operable_score = 25
    operable_issues = []
    
    # 2.1 キーボードアクセシビリティ
    if 'tabindex=' not in component_code and ('input' in component_code or 'button' in component_code):
        operable_issues.append("適切なタブインデックスが設定されていません")
        operable_score -= 5
    
    # 2.4 フォーカス表示
    if ':focus' not in component_code and 'input' in component_code:
        operable_issues.append("フォーカス状態のスタイルが設定されていません")
        operable_score -= 5
    
    compliance_result["categories"]["operable"]["score"] = operable_score
    compliance_result["categories"]["operable"]["issues"] = operable_issues
    
    # 3. 理解可能 (Understandable)
    understandable_score = 25
    understandable_issues = []
    
    # 3.1 ラベル
    if 'input' in component_code:
        if 'label' not in component_code and 'aria-label' not in component_code:
            understandable_issues.append("入力フィールドにラベルが設定されていません")
            understandable_score -= 5
    
    # 3.3 エラーメッセージ
    if 'error' in component_code.lower():
        if 'aria-describedby' not in component_code:
            understandable_issues.append("エラーメッセージが適切に関連付けられていません")
            understandable_score -= 3
    
    compliance_result["categories"]["understandable"]["score"] = understandable_score
    compliance_result["categories"]["understandable"]["issues"] = understandable_issues
    
    # 4. 堅牢性 (Robust)
    robust_score = 25
    robust_issues = []
    
    # 4.1 有効なHTML
    if '<template>' in component_code:
        # 簡単なHTML構造チェック
        template_match = re.search(r'<template>(.*?)</template>', component_code, re.DOTALL)
        if template_match:
            template_content = template_match.group(1)
            # 閉じタグの不整合をチェック
            open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)', template_content)
            close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)', template_content)
            if len(open_tags) != len(close_tags):
                robust_issues.append("HTMLタグの開閉が不整合です")
                robust_score -= 10
    
    compliance_result["categories"]["robust"]["score"] = robust_score
    compliance_result["categories"]["robust"]["issues"] = robust_issues
    
    # 総合スコア計算
    total_score = sum(cat["score"] for cat in compliance_result["categories"].values())
    compliance_result["score"] = total_score
    
    # レベル判定
    if total_score >= 90:
        compliance_result["overall_level"] = "AAA"
    elif total_score >= 70:
        compliance_result["overall_level"] = "AA"
    elif total_score >= 50:
        compliance_result["overall_level"] = "A"
    else:
        compliance_result["overall_level"] = "Non-compliant"
    
    return compliance_result

def heuristic_evaluation(component_code: str) -> Dict[str, Any]:
    """ニールセンの10のヒューリスティック評価"""
    
    evaluation_result = {
        "overall_score": 0,
        "heuristics": {}
    }
    
    heuristics = [
        ("visibility_of_system_status", "システム状態の視認性"),
        ("match_between_system_and_real_world", "システムと現実世界の合致"),
        ("user_control_and_freedom", "ユーザーコントロールと自由度"),
        ("consistency_and_standards", "一貫性と標準"),
        ("error_prevention", "エラー防止"),
        ("recognition_rather_than_recall", "記憶よりも認識"),
        ("flexibility_and_efficiency", "柔軟性と効率性"),
        ("aesthetic_and_minimalist_design", "美的で最小限のデザイン"),
        ("help_users_recognize_diagnose_recover", "エラー認識・診断・回復支援"),
        ("help_and_documentation", "ヘルプとドキュメント")
    ]
    
    for heuristic_key, heuristic_name in heuristics:
        score, issues = evaluate_heuristic(component_code, heuristic_key)
        evaluation_result["heuristics"][heuristic_key] = {
            "name": heuristic_name,
            "score": score,
            "max_score": 5,
            "issues": issues,
            "recommendations": generate_heuristic_recommendations(heuristic_key, issues)
        }
    
    # 総合スコア計算
    total_score = sum(h["score"] for h in evaluation_result["heuristics"].values())
    evaluation_result["overall_score"] = total_score / len(heuristics)
    
    return evaluation_result

def material_design_review(component_code: str) -> Dict[str, Any]:
    """Material Design準拠性レビュー"""
    
    review_result = {
        "overall_score": 0,
        "categories": {
            "color_system": {"score": 0, "max_score": 25, "issues": []},
            "typography": {"score": 0, "max_score": 25, "issues": []},
            "elevation": {"score": 0, "max_score": 25, "issues": []},
            "motion": {"score": 0, "max_score": 25, "issues": []}
        }
    }
    
    # Color System
    color_score = 25
    color_issues = []
    
    if not check_material_color_system(component_code):
        color_issues.append({
            "severity": "medium",
            "description": "Material Design色システムの使用が不十分です",
            "solution": "Primary, Secondary, Tertiary色を適切に使用してください"
        })
        color_score -= 5
    
    review_result["categories"]["color_system"]["score"] = max(0, color_score)
    review_result["categories"]["color_system"]["issues"] = color_issues
    
    # Typography
    typography_score = 25
    typography_issues = []
    
    if not check_material_typography(component_code):
        typography_issues.append({
            "severity": "medium",
            "description": "Material Designタイポグラフィシステムの使用が不十分です",
            "solution": "Display, Headline, Title, Body, Labelスタイルを適切に使用してください"
        })
        typography_score -= 5
    
    review_result["categories"]["typography"]["score"] = max(0, typography_score)
    review_result["categories"]["typography"]["issues"] = typography_issues
    
    # Elevation
    elevation_score = 25
    elevation_issues = []
    
    if not check_material_elevation(component_code):
        elevation_issues.append({
            "severity": "low",
            "description": "適切なエレベーション（影）の使用が不十分です",
            "solution": "Material Designのエレベーションガイドラインに従ってください"
        })
        elevation_score -= 3
    
    review_result["categories"]["elevation"]["score"] = max(0, elevation_score)
    review_result["categories"]["elevation"]["issues"] = elevation_issues
    
    # Motion
    motion_score = 25
    motion_issues = []
    
    if not check_material_motion(component_code):
        motion_issues.append({
            "severity": "low",
            "description": "Material Designモーションガイドラインの適用が不十分です",
            "solution": "適切なアニメーションと遷移を実装してください"
        })
        motion_score -= 3
    
    review_result["categories"]["motion"]["score"] = max(0, motion_score)
    review_result["categories"]["motion"]["issues"] = motion_issues
    
    # 総合スコア計算
    total_score = sum(cat["score"] for cat in review_result["categories"].values())
    review_result["overall_score"] = total_score
    
    return review_result

def comprehensive_evaluation(component_code: str, file_path: str = "component.vue") -> Dict[str, Any]:
    """総合評価とレポート生成"""
    
    # 各評価の実行
    component_analysis = vue_component_analysis(component_code, file_path)
    wcag_compliance = wcag_compliance_check(component_code)
    heuristic_eval = heuristic_evaluation(component_code)
    material_review = material_design_review(component_code)
    
    # 総合スコア計算
    scores = {
        "component_quality": component_analysis.get("ui_metrics", {}).get("maintainability_score", 0),
        "wcag_compliance": wcag_compliance["score"],
        "heuristic_evaluation": heuristic_eval["overall_score"] * 20,  # 5点満点を100点満点に変換
        "material_design": material_review["overall_score"]
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    # 改善提案の生成
    improvement_suggestions = generate_improvement_suggestions(
        wcag_compliance, heuristic_eval, material_review
    )
    
    # 優先度付けされた問題リスト
    prioritized_issues = prioritize_issues(
        wcag_compliance, heuristic_eval, material_review
    )
    
    return {
        "overall_score": round(overall_score, 2),
        "grade": get_grade(overall_score),
        "detailed_scores": scores,
        "component_analysis": component_analysis,
        "wcag_compliance": wcag_compliance,
        "heuristic_evaluation": heuristic_eval,
        "material_design_review": material_review,
        "improvement_suggestions": improvement_suggestions,
        "prioritized_issues": prioritized_issues,
        "summary": generate_evaluation_summary(overall_score, prioritized_issues)
    }

# ヘルパー関数の実装
def calculate_template_complexity(component_code: str) -> int:
    """テンプレートの複雑度を計算"""
    template_match = re.search(r'<template>(.*?)</template>', component_code, re.DOTALL)
    if not template_match:
        return 0
    
    template_content = template_match.group(1)
    
    # 複雑度の要素をカウント
    complexity = 0
    complexity += len(re.findall(r'v-if', template_content))  # 条件分岐
    complexity += len(re.findall(r'v-for', template_content))  # ループ
    complexity += len(re.findall(r'v-show', template_content))  # 表示制御
    complexity += len(re.findall(r'@\w+', template_content))  # イベントハンドラー
    complexity += len(re.findall(r'<\w+', template_content))  # HTML要素数
    
    return complexity

def analyze_component_structure(component_code: str) -> Dict[str, Any]:
    """コンポーネントの構造分析"""
    structure = {
        "has_template": "<template>" in component_code,
        "has_script": "<script" in component_code,
        "has_style": "<style" in component_code,
        "script_setup": "<script setup>" in component_code,
        "composition_api": "from 'vue'" in component_code,
        "props_defined": "defineProps" in component_code,
        "emits_defined": "defineEmits" in component_code,
        "slots_used": "<slot" in component_code
    }
    
    return structure

def detailed_accessibility_check(component_code: str) -> List[str]:
    """詳細なアクセシビリティチェック"""
    issues = []
    
    # ARIAラベルのチェック
    if 'input' in component_code and 'aria-label' not in component_code and 'id=' not in component_code:
        issues.append("入力フィールドにARIAラベルまたはIDが設定されていません")
    
    # ボタンのアクセシビリティ
    if 'button' in component_code and 'aria-describedby' not in component_code:
        issues.append("ボタンに説明が関連付けられていません")
    
    # フォーカス管理
    if 'tabindex=' in component_code:
        tabindex_values = re.findall(r'tabindex="(-?\d+)"', component_code)
        if any(int(val) > 0 for val in tabindex_values):
            issues.append("正の値のtabindexは推奨されません")
    
    return issues

def analyze_performance_indicators(component_code: str) -> Dict[str, Any]:
    """パフォーマンス指標の分析"""
    indicators = {
        "computed_properties": len(re.findall(r'computed:', component_code)),
        "watchers": len(re.findall(r'watch:', component_code)),
        "event_listeners": len(re.findall(r'@\w+', component_code)),
        "reactive_refs": len(re.findall(r'ref\(', component_code)),
        "template_refs": len(re.findall(r'ref="', component_code)),
        "potential_issues": []
    }
    
    # パフォーマンス上の問題を検出
    if indicators["event_listeners"] > 10:
        indicators["potential_issues"].append("イベントリスナーが多すぎます")
    
    if indicators["watchers"] > 5:
        indicators["potential_issues"].append("ウォッチャーが多すぎます")
    
    return indicators

def check_semantic_html(component_code: str) -> bool:
    """セマンティックHTMLの使用をチェック"""
    semantic_tags = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
    return any(tag in component_code for tag in semantic_tags)

def check_color_contrast(component_code: str) -> List[Dict[str, Any]]:
    """色コントラストのチェック"""
    issues = []
    # 実際の実装では色の抽出と計算が必要
    # 今回は簡略化
    return issues

def check_keyboard_accessibility(component_code: str) -> bool:
    """キーボードアクセシビリティのチェック"""
    # tabindex、aria-label、role属性の存在確認
    return any(attr in component_code for attr in ['tabindex', 'aria-label', 'role'])

def check_navigation_clarity(component_code: str) -> bool:
    """ナビゲーションの明確さをチェック"""
    # 見出しタグやaria-labelの存在確認
    return any(tag in component_code for tag in ['<h1', '<h2', '<h3', 'aria-label'])

def check_predictable_functionality(component_code: str) -> bool:
    """予測可能な機能性をチェック"""
    # 自動フォーカス移動や予期しない変更を検出
    return 'autoFocus' not in component_code and 'onChange' not in component_code

def check_form_accessibility(component_code: str) -> List[Dict[str, Any]]:
    """フォームアクセシビリティのチェック"""
    issues = []
    
    # 必須フィールドの表示
    if 'required' in component_code and 'aria-required' not in component_code:
        issues.append({
            "severity": "medium",
            "description": "必須フィールドにaria-required属性が不足しています",
            "solution": "aria-required='true'を追加してください"
        })
    
    return issues

def check_html_validity(component_code: str) -> bool:
    """HTML有効性のチェック"""
    # 基本的な構文チェック
    open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)', component_code)
    close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)', component_code)
    
    # 自己完結タグを除外
    self_closing = ['img', 'input', 'br', 'hr', 'meta', 'link']
    open_tags = [tag for tag in open_tags if tag not in self_closing]
    
    return len(open_tags) == len(close_tags)

def check_aria_usage(component_code: str) -> List[Dict[str, Any]]:
    """ARIA属性の使用をチェック"""
    issues = []
    
    # 不正なARIA属性の使用
    invalid_aria = re.findall(r'aria-[a-zA-Z]+', component_code)
    valid_aria = ['aria-label', 'aria-labelledby', 'aria-describedby', 'aria-hidden', 'aria-expanded']
    
    for aria in invalid_aria:
        if aria not in valid_aria:
            issues.append({
                "severity": "low",
                "description": f"不明なARIA属性: {aria}",
                "solution": "有効なARIA属性を使用してください"
            })
    
    return issues

def evaluate_heuristic(component_code: str, heuristic_key: str) -> tuple:
    """個別ヒューリスティックの評価"""
    score = 5  # 最高点から減点方式
    issues = []
    
    if heuristic_key == "visibility_of_system_status":
        # ローディング状態、進行状況の表示
        if 'loading' not in component_code and 'progress' not in component_code:
            issues.append("システム状態の表示が不足しています")
            score -= 2
    
    elif heuristic_key == "consistency_and_standards":
        # Vuetifyコンポーネントの一貫使用
        if '<button' in component_code and 'v-btn' not in component_code:
            issues.append("一貫性のため、v-btnの使用を推奨します")
            score -= 1
    
    elif heuristic_key == "error_prevention":
        # フォームバリデーション
        if '<form' in component_code and 'validation' not in component_code:
            issues.append("フォームバリデーションの実装を推奨します")
            score -= 1
    
    # 他のヒューリスティックも同様に実装...
    
    return max(1, score), issues

def generate_heuristic_recommendations(heuristic_key: str, issues: List[str]) -> List[str]:
    """ヒューリスティック別の推奨事項を生成"""
    recommendations = []
    
    if heuristic_key == "visibility_of_system_status":
        recommendations.append("ローディング状態やプログレスインジケーターを追加してください")
    
    elif heuristic_key == "consistency_and_standards":
        recommendations.append("Vuetifyコンポーネントを一貫して使用してください")
    
    # 他のヒューリスティックも同様に実装...
    
    return recommendations

def check_material_color_system(component_code: str) -> bool:
    """Material Designカラーシステムのチェック"""
    material_colors = ['primary', 'secondary', 'tertiary', 'surface', 'background']
    return any(color in component_code for color in material_colors)

def check_material_typography(component_code: str) -> bool:
    """Material Designタイポグラフィのチェック"""
    typography_classes = ['text-h1', 'text-h2', 'text-body-1', 'text-body-2', 'text-caption']
    return any(typo in component_code for typo in typography_classes)

def check_material_elevation(component_code: str) -> bool:
    """Material Designエレベーションのチェック"""
    elevation_classes = ['elevation-', 'v-card', 'v-sheet']
    return any(elev in component_code for elev in elevation_classes)

def check_material_motion(component_code: str) -> bool:
    """Material Designモーションのチェック"""
    motion_keywords = ['transition', 'animation', 'v-fade-transition', 'v-slide-transition']
    return any(motion in component_code for motion in motion_keywords)

def generate_improvement_suggestions(wcag_compliance: Dict, heuristic_eval: Dict, material_review: Dict) -> List[Dict[str, Any]]:
    """改善提案の生成"""
    suggestions = []
    
    # WCAG準拠の改善提案
    for category, data in wcag_compliance["categories"].items():
        for issue in data["issues"]:
            suggestions.append({
                "category": "WCAG 2.1",
                "priority": issue["severity"],
                "description": issue["description"],
                "solution": issue["solution"],
                "guideline": issue.get("guideline", "")
            })
    
    # ヒューリスティック評価の改善提案
    for heuristic, data in heuristic_eval["heuristics"].items():
        if data["score"] < 4:  # 4点未満の場合
            for recommendation in data["recommendations"]:
                suggestions.append({
                    "category": "ユーザビリティ",
                    "priority": "medium",
                    "description": f"{data['name']}: {recommendation}",
                    "solution": recommendation
                })
    
    return suggestions

def prioritize_issues(wcag_compliance: Dict, heuristic_eval: Dict, material_review: Dict) -> List[Dict[str, Any]]:
    """問題の優先度付け"""
    issues = []
    
    # 高優先度: WCAG準拠の重要な問題
    for category, data in wcag_compliance["categories"].items():
        for issue in data["issues"]:
            if issue["severity"] == "high":
                issues.append({
                    "priority": "高",
                    "category": "アクセシビリティ",
                    "description": issue["description"],
                    "solution": issue["solution"]
                })
    
    # 中優先度: ユーザビリティの問題
    for heuristic, data in heuristic_eval["heuristics"].items():
        if data["score"] < 3:  # 3点未満の場合
            issues.append({
                "priority": "中",
                "category": "ユーザビリティ",
                "description": f"{data['name']}の改善が必要",
                "solution": "ヒューリスティック評価に基づく改善"
            })
    
    return issues

def get_grade(score: float) -> str:
    """スコアに基づく評価等級"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def generate_evaluation_summary(overall_score: float, prioritized_issues: List[Dict]) -> str:
    """評価サマリーの生成"""
    grade = get_grade(overall_score)
    issue_count = len(prioritized_issues)
    
    summary = f"""
    ## 評価サマリー
    
    **総合評価: {grade}** (スコア: {overall_score:.1f}/100)
    
    **発見された問題: {issue_count}件**
    - 高優先度: {len([i for i in prioritized_issues if i['priority'] == '高'])}件
    - 中優先度: {len([i for i in prioritized_issues if i['priority'] == '中'])}件
    - 低優先度: {len([i for i in prioritized_issues if i['priority'] == '低'])}件
    
    **主な改善領域:**
    {', '.join(set(issue['category'] for issue in prioritized_issues[:5]))}
    """
    
    return summary.strip()

def find_line_number(content: str, search_term: str) -> int:
    """コンテンツ内での行番号を検索"""
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if search_term in line:
            return i
    return 0

def create_evaluation_agent():
    """評価エージェントを作成"""
    
    # ツールを作成
    analysis_tool = FunctionTool(func=vue_component_analysis)
    wcag_tool = FunctionTool(func=wcag_compliance_check)
    
    # エージェントを作成
    agent = Agent(
        name="evaluation_agent",
        model="gemini-1.5-flash-8b",
        description="Vue.jsコンポーネントの包括的な評価を行い、WCAG 2.1準拠性とユーザビリティを詳細に分析する専門エージェント",
        instruction=create_evaluation_instruction(),
        tools=[analysis_tool, wcag_tool]
    )
    
    return agent 