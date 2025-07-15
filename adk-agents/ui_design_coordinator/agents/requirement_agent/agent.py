from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import FunctionTool
from .prompt import REQUIREMENT_AGENT_INSTRUCTION

# 環境変数を読み込み
load_dotenv()

def analyze_user_requirements(user_input: str) -> dict:
    """ユーザーの要求を分析し、構造化された要件に変換する"""
    
    # 仮の実装 - 後で詳細を追加
    return {
        "status": "success",
        "structured_requirements": {
            "functional_requirements": ["ユーザー登録機能", "ログイン機能"],
            "non_functional_requirements": ["レスポンシブデザイン", "アクセシビリティ対応"],
            "ui_requirements": ["モダンなデザイン", "直感的な操作"],
            "technical_requirements": ["Vue.js 3", "Vuetify 3"]
        },
        "priority": "high",
        "estimated_complexity": "medium"
    }

def create_specification_document(requirements: dict) -> dict:
    """要件から仕様書を生成する"""
    
    # 仮の実装 - 後で詳細を追加
    return {
        "status": "success",
        "specification": {
            "title": "UI/UX設計仕様書",
            "version": "1.0",
            "requirements": requirements,
            "acceptance_criteria": ["要件を満たすこと", "ユーザビリティテストをクリアすること"]
        }
    }

def create_requirement_agent(artifact_service=None):
    """要件整理エージェントを作成"""
    
    # ツールを作成
    analyze_tool = FunctionTool(func=analyze_user_requirements)
    specification_tool = FunctionTool(func=create_specification_document)
    
    # エージェントを作成
    agent = Agent(
        name="requirement_agent",
        model="gemini-1.5-flash-8b",
        description="ユーザーの要求を分析し、構造化された要件に変換する専門エージェント",
        instruction=REQUIREMENT_AGENT_INSTRUCTION,
        tools=[analyze_tool, specification_tool]
    )
    
    return agent 