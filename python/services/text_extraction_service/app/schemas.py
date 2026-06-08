from typing import List

from pydantic import BaseModel


class ExtractRequest(BaseModel):
    file: str


class PageContent(BaseModel):
    page_number: int
    content: str


class ExtractResponse(BaseModel):
    pages: List[PageContent]
