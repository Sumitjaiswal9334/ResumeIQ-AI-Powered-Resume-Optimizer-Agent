"""Small LangGraph workflow used by the app for structured, inspectable analysis."""
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from resume_optimizer import match_resume_to_job, analyze_resume

class OptimizerState(TypedDict, total=False):
    resume_text: str
    job_description: str
    job_title: str
    company: str
    candidate_name: str
    model: str
    match: dict[str, Any]
    result: dict[str, Any]

def score_node(state: OptimizerState):
    return {"match": match_resume_to_job(
        state["resume_text"], state["job_description"],
        state.get("job_title", ""), state.get("company", "")
    )}

def review_node(state: OptimizerState):
    return {"result": analyze_resume(
        state["resume_text"], state["job_description"],
        state.get("job_title", ""), state.get("company", ""),
        state.get("model", "gemini-3.5-flash-lite"), state.get("candidate_name", "")
    )}

workflow = StateGraph(OptimizerState)
workflow.add_node("score", score_node)
workflow.add_node("review", review_node)
workflow.add_edge(START, "score")
workflow.add_edge("score", "review")
workflow.add_edge("review", END)
optimizer_graph = workflow.compile()
