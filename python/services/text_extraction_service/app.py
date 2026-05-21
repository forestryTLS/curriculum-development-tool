import os
import base64
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3

app = FastAPI(title='Text Extraction Service', version='1.0.0')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

textract = boto3.client('textract', region_name=os.environ.get('AWS_REGION', 'us-west-2'))


class ExtractRequest(BaseModel):
    file: str


class PageContent(BaseModel):
    page_number: int
    content: str


class ExtractResponse(BaseModel):
    pages: list[PageContent]


@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.post('/extract', response_model=ExtractResponse)
async def extract(request: ExtractRequest):
    try:
        file_bytes = base64.b64decode(request.file)

        logger.info(f'Extracting text from {len(file_bytes)} byte document')
        response = textract.detect_document_text(Document={'Bytes': file_bytes})

        pages = {}
        for block in response['Blocks']:
            if block['BlockType'] == 'PAGE':
                page_num = block['Page']
                pages[page_num] = {'page_number': page_num, 'content': ''}

        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                page_num = block['Page']
                if page_num in pages:
                    pages[page_num]['content'] += block['Text'] + '\n'

        result = sorted(pages.values(), key=lambda p: p['page_number'])
        logger.info(f'Extracted {len(result)} pages')

        return ExtractResponse(pages=result)

    except Exception as e:
        logger.error(f'Extraction failed: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))
