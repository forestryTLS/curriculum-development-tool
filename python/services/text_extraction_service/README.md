# Text Extraction Service

FastAPI microservice for extracting text from PDFs using AWS Textract. Called by Laravel's `IndexCourseMaterial` job when users select the AWS Textract extraction engine.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   ```
   Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

   The remaining values should already be set to 
   ```
   AWS_REGION=ca-central-1
   AWS_S3_BUCKET=text-extraction-temp
   PORT=5000
   ```

4. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 5000 --reload
   ```
   API docs at `http://127.0.0.1:5000/docs`

## AWS Configuration

An S3 bucket for temporary file storage called `text-extraction-temp` should already be created. Check with:
```bash
aws s3 ls s3://text-extraction-temp/
```

If not, set it up:
```bash
# Create the bucket
aws s3 mb s3://text-extraction-temp --region ca-central-1

#Set bucket lifecycle policy to delete files after 1 day:
aws s3api put-bucket-lifecycle-configuration --bucket text-extraction-temp --lifecycle-configuration '{"Rules":[{"Status":"Enabled","Prefix":"textract-jobs/","ExpirationInDays":1}]}'
```

## How It Works

Attempts synchronous extraction first (faster, no polling needed). Synchronous extraction only works for single-page PDFs, so we check that the file size is under 5MB as an approximate indicator for single-page documents. If that fails or file is larger, falls back to asynchronous extraction. This microservice handles the polling for the asynchronous operation internally, and returns results synchronously to Laravel regardless of which method was used.

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
