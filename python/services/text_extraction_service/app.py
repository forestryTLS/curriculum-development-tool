import os
import base64
import logging
import time
import io
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import boto3

load_dotenv()

app = FastAPI(title='Text Extraction Service', version='1.0.0')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

textract = boto3.client('textract', region_name=os.environ.get('AWS_REGION', 'us-west-2'))
s3 = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-west-2'))

BUCKET_NAME = os.environ.get('AWS_S3_BUCKET', 'text-extraction-temp')


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

        # Verify it looks like a PDF
        if not file_bytes.startswith(b'%PDF'):
            logger.warning(f'File does not start with PDF magic bytes. Starts with: {file_bytes[:10]}')

        # For small single-page PDFs, try synchronous operation first
        if len(file_bytes) < 5 * 1024 * 1024:  # < 5MB
            try:
                response = textract.detect_document_text(Document={'Bytes': file_bytes})
                pages = extract_pages_from_response(response)
                logger.info(f'Extracted {len(pages)} pages using synchronous operation')
                return ExtractResponse(pages=pages)
            except Exception as e:
                logger.info(f'Synchronous operation failed: {str(e)}, falling back to async')

        # Use asynchronous operation for larger files or if sync fails
        # Upload to S3 first (async requires S3 location)
        s3_key = f'textract-jobs/{int(time.time())}-{os.urandom(4).hex()}.pdf'
        s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_bytes)
        logger.info(f'Uploaded file to s3://{BUCKET_NAME}/{s3_key}')

        logger.info(f'Textract region: {textract.meta.region_name}')
        logger.info(f'S3 region: {s3.meta.region_name}')
        logger.info(f'Starting async detection for Bucket={BUCKET_NAME}, Key={s3_key}')

        response = textract.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': BUCKET_NAME, 'Name': s3_key}}
        )
        job_id = response['JobId']
        logger.info(f'Started async text detection job: {job_id}')

        # Poll for job completion
        pages = wait_for_job_completion(job_id)
        logger.info(f'Extracted {len(pages)} pages using asynchronous operation')

        return ExtractResponse(pages=pages)

    except Exception as e:
        logger.error(f'Extraction failed: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


def extract_pages_from_response(response):
    """Extract pages and text from Textract response"""
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

    return sorted(pages.values(), key=lambda p: p['page_number'])


def wait_for_job_completion(job_id, max_wait_seconds=600):
    """Poll for async job completion and extract results"""
    start_time = time.time()
    max_wait = max_wait_seconds

    while time.time() - start_time < max_wait:
        response = textract.get_document_text_detection(JobId=job_id)
        status = response['JobStatus']

        logger.info(f'Job {job_id} status: {status}')

        if status == 'SUCCEEDED':
            # Collect results from all pages
            pages = {}
            next_token = None

            while True:
                if next_token:
                    response = textract.get_document_text_detection(JobId=job_id, NextToken=next_token)
                else:
                    response = textract.get_document_text_detection(JobId=job_id)

                for block in response['Blocks']:
                    if block['BlockType'] == 'PAGE':
                        page_num = block['Page']
                        if page_num not in pages:
                            pages[page_num] = {'page_number': page_num, 'content': ''}

                    elif block['BlockType'] == 'LINE':
                        page_num = block['Page']
                        if page_num in pages:
                            pages[page_num]['content'] += block['Text'] + '\n'

                next_token = response.get('NextToken')
                if not next_token:
                    break

            return sorted(pages.values(), key=lambda p: p['page_number'])

        elif status == 'FAILED':
            raise Exception(f'Textract job {job_id} failed')

        # Wait before polling again
        time.sleep(2)

    raise Exception(f'Textract job {job_id} did not complete within {max_wait} seconds')
