from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.schemas import OutcomeMappingRequest, OutcomeMappingResponse
from app.services import MappingProcessor


app = FastAPI(
    title="Learning Outcome Mapping Service",
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


@app.post("/map-program-outcomes", response_model=OutcomeMappingResponse)
async def map_program_outcomes(
    request: OutcomeMappingRequest,
) -> OutcomeMappingResponse:
    processor = MappingProcessor(request)
    return processor.process()
