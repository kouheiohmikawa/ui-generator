"""
UI Design Coordinator – Root Agent
Orchestrates the specialist agents (requirement, design, evaluation, improvement) as described in the README.
"""

from dotenv import load_dotenv

from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import FunctionTool

from .root_agent_prompt import PROMPT

# Specialist agent factories
from ui_design_coordinator.agents.requirement_agent import create_requirement_agent
from ui_design_coordinator.agents.design_agent import create_design_agent
from ui_design_coordinator.agents.evaluation_agent import create_evaluation_agent
from ui_design_coordinator.agents.improvement_agent import create_improvement_agent

# Direct import of Design-Agent-specific tools (Vue component helpers)
from ui_design_coordinator.agents.design_agent.tools import (
    list_vue_components_in_artifacts,
    get_vue_component_from_artifacts,
    save_all_vue_files_to_artifacts,
)

load_dotenv()

requirement_agent = create_requirement_agent()
design_agent = create_design_agent()
evaluation_agent = create_evaluation_agent()
improvement_agent = create_improvement_agent()

requirement_tool = AgentTool(agent=requirement_agent)
design_tool = AgentTool(agent=design_agent)
evaluation_tool = AgentTool(agent=evaluation_agent)
improvement_tool = AgentTool(agent=improvement_agent)

root_agent = Agent(
    name="ui_design_coordinator",
    model="gemini-1.5-flash-8b",
    description="UI/UX設計と評価を行う専門エージェントチームのコーディネーター",
    instruction=PROMPT,
    tools=[
        requirement_tool,
        design_tool,
        evaluation_tool,
        improvement_tool,
        FunctionTool(func=save_all_vue_files_to_artifacts),
        FunctionTool(func=list_vue_components_in_artifacts),
        FunctionTool(func=get_vue_component_from_artifacts),
    ],
)

# Public re-export
__all__ = ["root_agent"]