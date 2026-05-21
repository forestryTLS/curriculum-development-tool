# Text Extraction Service

A FastAPI microservice that extracts text from PDF files using AWS Textract. Runs independently from the Laravel application and can be scaled separately. Includes automatic API documentation at `/docs`.

## Setup

### Local Development

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

2. Copy `.env.example` to `.env` and update with your AWS credentials:
   ```bash
   cp .env.example .env
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the service:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 5000 --reload
   ```

   The service will listen on `http://127.0.0.1:5000`.
   
   View interactive API docs at `http://127.0.0.1:5000/docs`

### Docker

Build and run with Docker:

```bash
docker build -t text-extraction-service .
docker run -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... -e AWS_REGION=us-west-2 -p 5000:5000 text-extraction-service
```

## AWS Setup

1. Create an IAM user or use an existing one with permissions for Textract
2. Attach the `AmazonTextractFullAccess` policy (or create a custom policy limiting to your needs)
3. Generate access keys and add to `.env`

## API Endpoints

### POST `/extract`

Extracts text from a PDF file.

**Request:**
```json
{
  "file": "base64-encoded-pdf-bytes"
}
```

**Response:**
```json
{
  "pages": [
    {
      "page_number": 1,
      "content": "Extracted text from page 1..."
    },
    {
      "page_number": 2,
      "content": "Extracted text from page 2..."
    }
  ]
}
```

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Integration with Laravel

The Laravel application calls this service from the `IndexCourseMaterial` job when a user selects "AWS Textract" as the extraction engine during upload.

Configure the service URL in `.env`:
```
TEXT_EXTRACTION_SERVICE_URL=http://text-extraction-service:5000
```

## Costs

AWS Textract pricing (as of 2026):
- ~$1.50 per 1000 pages
- For a 120-page document: ~$0.18

No monthly minimum. Free tier available for testing.

## Future Enhancements

- Support for other extraction engines (PyMuPDF, pdfplumber)
- Configurable engine selection via environment variable
- Caching of extraction results
- Async job status tracking
