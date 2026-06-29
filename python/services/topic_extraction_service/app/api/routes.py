from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas import ExtractRequest, ExtractResponse

from app.services import yake_extractor as extractor
# from app.services import bertopic_extractor as extractor
from app.services import preprocessor
from app.services import postprocessor


app = FastAPI(
    title="Topic Extraction Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
async def extract(request: ExtractRequest) -> ExtractResponse:
    text = ". \f".join(page.content for page in request.pages if page.content) # TODO: Move to preprocessor
    try:
        preprocessed_text = preprocessor.process(text)
        topics = extractor.extract(preprocessed_text)
        postprocessed_topics = postprocessor.process(topics)
        return ExtractResponse(topics=postprocessed_topics)
    except Exception as e:
        logger.error(f"Topic extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
