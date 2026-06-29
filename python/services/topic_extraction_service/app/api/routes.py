import base64

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas import ExtractRequest, ExtractResponse

from app.services import yake_extractor as extractor
# from app.services import bertopic_extractor as extractor
from app.services import preprocessor
from app.services import postprocessor
from app.services import powerpoint_processor


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
        if request.material_type.lower() == "slides" and request.file:
            topics = powerpoint_processor.extract(base64.b64decode(request.file))
        else:
            topics = extractor.extract(preprocessed_text)
        topics = postprocessor.process(topics)

        # if request.material_type.lower() == "slides" and request.file:
        #     slide_topics = powerpoint_processor.extract(base64.b64decode(request.file))
        #     if slide_topics:
        #         topics = postprocessor.union(slide_topics, topics)

        return ExtractResponse(topics=topics)
    except Exception as e:
        logger.error(f"Topic extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
