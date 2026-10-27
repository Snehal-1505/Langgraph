"""Checkpointing configuration for LangGraph workflows."""
from langgraph.checkpoint.memory import MemorySaver

# Persistent / In-memory checkpointer provider
# MemorySaver stores execution threads in memory for resumability and step history
_memory_checkpointer = MemorySaver()


def get_checkpointer():
    """Return the active checkpointer for the LangGraph workflow."""
    return _memory_checkpointer
