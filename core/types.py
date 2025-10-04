from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class Comment(BaseModel):
    body: str
    line: int
    side: str


class Review(BaseModel):
    file: str = Field(..., description="The file being reviewed")
    comments: List[Comment]


class DiffIssue(BaseModel):
    """Individual issue found in the diff"""

    type: str = Field(..., description="Type of issue: error, warning, or suggestion")
    line: str = Field(..., description="Line number or range where the issue occurs")
    message: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity level: high, medium, or low")
    file: str = Field(..., description="File path where the issue occurs")


class PRReviewResponse(BaseModel):
    """PR Review LLM response model for diff analysis"""

    issues: List[DiffIssue] = Field(
        default_factory=list, description="List of issues found in the diff"
    )
    summary: str = Field(..., description="Overall assessment of the changes")
