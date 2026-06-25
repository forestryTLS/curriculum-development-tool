from typing import List

from pydantic import BaseModel


class PageContent(BaseModel):
    page_number: int
    content: str


class ExtractRequest(BaseModel):
    pages: List[PageContent]


class Topic(BaseModel):
    topic: str
    score: float


class ExtractResponse(BaseModel):
    topics: List[Topic]
