from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import logger

from app.schemas import (
    OutcomeMappingRequest,
    OutcomeMappingResponse,
)
from app.services import BatchTransformInputBuilder, LOMappingRequestDynamoDBRecord


lo_mapping_request_store = LOMappingRequestDynamoDBRecord()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        lo_mapping_request_store.ensure_table_exists()
        logger.info("DynamoDB table ready")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise e
    yield


app = FastAPI(
    title="Learning Outcome Mapping Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
async def map_program_outcomes(request: OutcomeMappingRequest,) -> OutcomeMappingResponse:
    try:
        batchTranformInputBuilder = BatchTransformInputBuilder(request)
        s3_input_path = batchTranformInputBuilder.build_batch_prompt_records()
        lo_mapping_request_store.create_request(
            course_id=request.course_id,
            program_id=request.program_id,
            input_s3_path=s3_input_path,
            status="pending",
        )
        return batchTranformInputBuilder.process()
    except Exception as e:
        logger.error(f"Error in mapping LOs: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong while processing mapping request")
