# acekit/models.py
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ActionRecord(BaseModel):
"""One tool call or step taken by the agent.

This is intentionally generic: it works for browser tools, APIs, DB queries, etc.
"""

tool: str
args: Dict[str, Any] = Field(default_factory=dict)
result_type: str = Field(default="ok") # "ok" | "soft_fail" | "hard_fail"
error_category: str = Field(default="none") # e.g. "timeout", "api_error", etc.
message: str = Field(default="")
latency_ms: int = Field(default=0)
url: Optional[str] = None
retries: int = Field(default=0)


class RunEntry(BaseModel):
"""Stored representation of a single agent run."""

task: str
outcome: str
actions: List[Dict[str, Any]]
errors: List[str] = Field(default_factory=list)
preferences: List[str] = Field(default_factory=list)

goal_status: str = Field(default="unknown") # success | partial | failed | blocked | unknown
reason_for_status: str = Field(default="")
answer_relevance_score: float = Field(default=0.0)

used_tip_ids: List[str] = Field(default_factory=list)
domain: str = Field(default="default")

signature: List[str] = Field(default_factory=list)

created_at: datetime = Field(default_factory=datetime.utcnow)


class Tip(BaseModel):
"""One reusable bullet of guidance that ACE can inject into prompts."""

id: str
domain: str = Field(default="default")
task_signature: List[str] = Field(default_factory=list)

tip: str
category: str = Field(default="general")

confidence: float = Field(default=0.5)
helpful_count: int = Field(default=0)
harmful_count: int = Field(default=0)

created_at: datetime = Field(default_factory=datetime.utcnow)
last_used: Optional[datetime] = None
