from typing import List, Optional

from pydantic import BaseModel


class PageContent(BaseModel):
    page_number: int
    content: str


class ExtractRequest(BaseModel):
    pages: List[PageContent]
    material_type: Optional[str] = None
    file: Optional[str] = None


class Topic(BaseModel):
    topic: str
    score: float


class ExtractResponse(BaseModel):
    topics: List[Topic]