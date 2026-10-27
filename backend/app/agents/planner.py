import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from app.tools.llm_provider import get_llm

logger = logging.getLogger(__name__)


class TaskPlan(BaseModel):
    task_id: str = Field(..., description="Unique task identifier, e.g. task_trends, task_benefits, task_risks")
    task_title: str = Field(..., description="Descriptive title for this research perspective")
    perspective: str = Field(..., description="Role: 'trends', 'benefits', or 'risks'")
    research_objective: str = Field(..., description="Specific goal of this sub-investigation")
    search_queries: List[str] = Field(..., min_length=1, description="Targeted web search queries to find real empirical evidence")
    expected_evidence: str = Field(..., description="Specific types of data, facts, or studies expected")
    priority: int = Field(1, ge=1, le=5, description="Priority score from 1 (highest) to 5")


class ResearchPlan(BaseModel):
    main_question: str = Field(..., description="Refined primary research question")
    scope_clarification: str = Field(..., description="Boundaries and limitations of this research")
    tasks: List[TaskPlan] = Field(..., min_length=3, max_length=3, description="Exactly 3 parallel research tasks covering trends, benefits, and risks")


PLANNER_SYSTEM_PROMPT = """You are the Senior Research Planning Agent for ResearchLab AI.
Your purpose is to break down the user's research topic into a rigorous, balanced, 3-perspective research plan.

MANDATORY RULES:
1. You MUST generate exactly 3 distinct, non-redundant research tasks:
   - Task 1 (trends): Current developments, verified facts, adoption metrics, and emerging trends.
   - Task 2 (benefits): Practical benefits, productivity gains, real-world opportunities, and application cases.
   - Task 3 (risks): Limitations, employment/workforce impacts, security/hallucination risks, disagreements, and ethical concerns.
2. Formulate 2-3 precise search queries for each task that are likely to find factual articles, industry benchmarks, and empirical studies.
3. Establish clear scope and limitations. Do NOT allow arbitrary code generation or command execution.
"""


class PlannerAgent:
    def __init__(self, llm=None):
        self.llm = llm or get_llm(temperature=0.1)

    async def create_plan(self, topic: str, scope: Optional[str] = None, depth: str = "standard") -> ResearchPlan:
        """Create a validated 3-task research plan."""
        human_text = f"Research Topic: {topic}\n"
        if scope:
            human_text += f"Additional Context/Scope: {scope}\n"
        human_text += f"Research Depth: {depth}\n"
        human_text += "Generate the 3-perspective research plan with search queries and expected evidence."

        try:
            # Attempt structured output if supported by model
            if hasattr(self.llm, "with_structured_output"):
                structured_model = self.llm.with_structured_output(ResearchPlan)
                result = await structured_model.ainvoke([
                    SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                    HumanMessage(content=human_text)
                ])
                if isinstance(result, ResearchPlan):
                    return result

            # Fallback direct generation
            resp = await self.llm.ainvoke([
                SystemMessage(content=PLANNER_SYSTEM_PROMPT + "\nRespond with valid JSON adhering to the ResearchPlan schema."),
                HumanMessage(content=human_text)
            ])
            import json
            data = json.loads(resp.content)
            return ResearchPlan.model_validate(data)
        except Exception as e:
            logger.warning(f"Structured planner generation encountered: {e}. Generating fallback plan.")
            return self._fallback_plan(topic, scope)

    def _fallback_plan(self, topic: str, scope: Optional[str] = None) -> ResearchPlan:
        """Deterministic reliable plan fallback."""
        clean_topic = topic.strip()
        return ResearchPlan(
            main_question=clean_topic,
            scope_clarification=scope or f"Investigation of core dimensions of {clean_topic}.",
            tasks=[
                TaskPlan(
                    task_id="task_trends",
                    task_title="Current Developments, Facts & Trends",
                    perspective="trends",
                    research_objective=f"Identify recent breakthroughs, industry adoption statistics, and verifiable facts regarding {clean_topic}.",
                    search_queries=[
                        f"{clean_topic} latest developments statistics 2024 2025 2026",
                        f"{clean_topic} industry adoption current trends research"
                    ],
                    expected_evidence="Adoption percentages, industry reports, verified timeline of advances.",
                    priority=1
                ),
                TaskPlan(
                    task_id="task_benefits",
                    task_title="Benefits, Opportunities & Productivity",
                    perspective="benefits",
                    research_objective=f"Evaluate measured benefits, operational efficiencies, and practical opportunities from {clean_topic}.",
                    search_queries=[
                        f"{clean_topic} productivity benefits empirical case studies",
                        f"{clean_topic} practical applications advantages"
                    ],
                    expected_evidence="Productivity metrics, case study outcomes, workflow enhancements.",
                    priority=1
                ),
                TaskPlan(
                    task_id="task_risks",
                    task_title="Risks, Limitations & Challenges",
                    perspective="risks",
                    research_objective=f"Examine technical limitations, workforce/employment impact, security risks, and controversies surrounding {clean_topic}.",
                    search_queries=[
                        f"{clean_topic} risks limitations employment impact challenges",
                        f"{clean_topic} security drawbacks controversies"
                    ],
                    expected_evidence="Known failure modes, employment transition findings, security concerns.",
                    priority=1
                )
            ]
        )
