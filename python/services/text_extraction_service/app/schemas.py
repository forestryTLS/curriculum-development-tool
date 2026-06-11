from typing import List

from pydantic import BaseModel


class ExtractRequest(BaseModel):
    file: str


class PageContent(BaseModel): 
    # TODO: page_number is only needed for processing with textract, 
    #       so we could relace PageContent to just str when returning results
    page_number: int
    content: str


class ExtractResponse(BaseModel):
    pages: List[PageContent]
