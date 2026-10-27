import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from app.tools.web_search import WebSearchProvider
from app.tools.page_reader import PageReader
from app.tools.llm_provider import get_llm
from app.agents.planner import TaskPlan

logger = logging.getLogger(__name__)


class FindingItem(BaseModel):
    task_id: str
    claim: str = Field(..., description="Factual claim or insight derived from the source")
    source_title: str
    source_url: str
    domain: str
    evidence_passage: str = Field(..., description="Direct excerpt or paraphrased evidence from retrieved content")
    publication_date: Optional[str] = None
    retrieval_timestamp: datetime = Field(default_factory=datetime.utcnow)
    relevance_explanation: str = Field(default="Directly relevant empirical evidence", description="Why the source is relevant")
    limitations: Optional[str] = None


class SourceItem(BaseModel):
    url: str
    title: str
    domain: str
    publication_date: Optional[str] = None
    retrieval_timestamp: datetime = Field(default_factory=datetime.utcnow)
    extracted_evidence: str
    status: str = "retrieved"


class ResearcherResult(BaseModel):
    task_id: str
    perspective: str
    findings: List[FindingItem] = Field(default_factory=list)
    sources: List[SourceItem] = Field(default_factory=list)
    summary: str = ""


RESEARCHER_SYNTHESIS_PROMPT = """You are a Specialized Research Agent for ResearchLab AI.
Perspective: {perspective}
Research Objective: {objective}

Analyze the raw web excerpts below collected for this task.
MANDATORY RULES:
1. Extract 2 to 4 factual findings that strictly originate from the provided excerpts.
2. DO NOT invent citations, URLs, statistics, or dates.
3. If an excerpt is insufficient, state the limitation clearly.
4. Ground every claim directly in the source URL provided.
"""


class ResearcherAgent:
    def __init__(self, search_provider: Optional[WebSearchProvider] = None, page_reader: Optional[PageReader] = None, llm=None):
        self.search_provider = search_provider or WebSearchProvider()
        self.page_reader = page_reader or PageReader()
        self.llm = llm or get_llm(temperature=0.1)

    async def execute_task(self, task: TaskPlan, max_sources: int = 4) -> ResearcherResult:
        """
        Execute research for a single perspective task:
        1. Run web searches across queries
        2. Deduplicate URLs
        3. Fetch readable content safely
        4. Synthesize verifiable findings
        """
        logger.info(f"Starting research task: {task.task_id} ({task.perspective})")
        seen_urls = set()
        raw_sources: List[Dict[str, Any]] = []

        # 1. Search across queries
        for query in task.search_queries[:2]:
            try:
                results = await self.search_provider.search(query, max_results=max_sources)
                for res in results:
                    url = res.get("url")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        raw_sources.append(res)
            except Exception as e:
                logger.warning(f"Search query '{query}' failed: {e}")

        # Limit sources
        selected_sources = raw_sources[:max_sources]

        # 2. Fetch page content concurrently with bounded semaphore
        semaphore = asyncio.Semaphore(3)

        async def _fetch(src):
            async with semaphore:
                url = src.get("url")
                page_data = await self.page_reader.fetch_page(url)
                return {**src, **page_data}

        fetched_results = await asyncio.gather(*[_fetch(s) for s in selected_sources], return_exceptions=True)

        sources_list: List[SourceItem] = []
        findings_list: List[FindingItem] = []
        context_excerpts = []

        for item in fetched_results:
            if isinstance(item, Exception) or not isinstance(item, dict):
                continue
            
            url = item.get("url", "")
            title = item.get("title") or url
            domain = item.get("domain", "")
            text = item.get("text", "") or item.get("snippet", "")
            pub_date = item.get("publication_date")
            status = item.get("status", "retrieved")

            if text:
                excerpt = text[:1500]
                sources_list.append(SourceItem(
                    url=url,
                    title=title,
                    domain=domain,
                    publication_date=pub_date,
                    extracted_evidence=excerpt,
                    status=status
                ))
                context_excerpts.append(f"Source: {title}\nURL: {url}\nDate: {pub_date}\nExcerpt: {excerpt}\n")

        # 3. If sources were found, extract findings with LLM or deterministic fallback
        if context_excerpts:
            findings_list = await self._synthesize_findings(task, context_excerpts, sources_list)
        else:
            # Document lack of available evidence
            findings_list.append(FindingItem(
                task_id=task.task_id,
                claim=f"No direct web sources could be retrieved for '{task.task_title}'.",
                source_title="N/A - Search Offline or Unavailable",
                source_url="https://offline.local/no-sources",
                domain="offline.local",
                evidence_passage="Web search yielded no accessible public pages within safety and timeout boundaries.",
                relevance_explanation="Transparent indication of research limitations.",
                limitations="Absence of empirical web data."
            ))

        return ResearcherResult(
            task_id=task.task_id,
            perspective=task.perspective,
            findings=findings_list,
            sources=sources_list,
            summary=f"Collected {len(sources_list)} sources and {len(findings_list)} findings for {task.task_title}."
        )

    async def _synthesize_findings(self, task: TaskPlan, excerpts: List[str], sources: List[SourceItem]) -> List[FindingItem]:
        """Synthesize structured findings from source excerpts."""
        combined_text = "\n---\n".join(excerpts[:4])
        prompt = (
            RESEARCHER_SYNTHESIS_PROMPT.format(perspective=task.perspective, objective=task.research_objective)
            + f"\n\nExcerpts:\n{combined_text}"
        )

        try:
            class FindingsOutput(BaseModel):
                items: List[FindingItem]

            if hasattr(self.llm, "with_structured_output"):
                structured = self.llm.with_structured_output(FindingsOutput)
                res = await structured.ainvoke([HumanMessage(content=prompt)])
                if isinstance(res, FindingsOutput) and res.items:
                    # Ensure task_id is set
                    for f in res.items:
                        f.task_id = task.task_id
                    return res.items
        except Exception as e:
            logger.warning(f"Structured finding extraction failed: {e}. Using deterministic extraction.")

        # Deterministic extraction fallback: Ground strictly in each source
        findings = []
        for src in sources[:3]:
            evidence_snippet = src.extracted_evidence[:300].strip()
            if not evidence_snippet:
                continue
            findings.append(FindingItem(
                task_id=task.task_id,
                claim=f"Observed in {src.title}: {evidence_snippet[:120]}...",
                source_title=src.title,
                source_url=src.url,
                domain=src.domain,
                evidence_passage=evidence_snippet,
                publication_date=src.publication_date,
                relevance_explanation=f"Directly relevant to perspective '{task.perspective}'.",
                limitations="Paraphrased from primary retrieved webpage."
            ))
        return findings
