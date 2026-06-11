# FastAPI Text Extraction Service

# Overview

Performs OCR on PDF files using AWS Textract, and returns page-wise extracted text. 

All PDF pages are scanned as images, and already searchable text will still be read with OCR.

## AWS Configuration

This should already be set up for the temp PDF bucket. But if you create a new bucket, set the bucket lifecycle policy to delete files after 1 day, so they don't unnecessarily take up S3 space. Replace `text-extraction-temp` with the bucket name.

```
aws s3api put-bucket-lifecycle-configuration --bucket text-extraction-temp --lifecycle-configuration '{"Rules":[{"Status":"Enabled","Prefix":"textract-jobs/","ExpirationInDays":1}]}'
```

## How It Works

- Synchronous OCR extraction: single-page PDF, doesn't need to be uploaded to S3
- Asynchronous OCR extraction: multi-page PDF, needs to be uploaded to S3

Checks PDF page count, and if 1 page, tries synchronous OCR first. If more than one page, or synchronous failed, tries asynchronous instead, polling every `POLLING_INTERVAL_SECONDS` seconds for a response from AWS Textract.

## API

**POST `/extract`**: Extract text from base64-encoded PDF
```json
{
  "file": "base64-encoded-pdf-bytes"
}
```

Returns:
```json
{
  "pages": [
    {"page_number": 1, "content": "..."},
    {"page_number": 2, "content": "..."}
  ]
}
```

**GET `/health`**: Health check endpoint
