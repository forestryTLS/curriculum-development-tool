from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import logger
import json
import os


from app.schemas import (
    OutcomeMappingRequest,
    ManualProcessRequest
)
from app.services import BatchTransformInputBuilder, LOMappingRequestDynamoDBRecord, process_batch_transform_results
from app.services.scheduled_job import create_scheduler
from app.services.process_batch_transform_results import process_records


lo_mapping_request_store = LOMappingRequestDynamoDBRecord()
boto_session = lo_mapping_request_store._create_boto_session()
REGION = os.environ.get("AWS_REGION", "ca-central-1")
lambda_client = boto_session.client("lambda", region_name=REGION)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        lo_mapping_request_store.ensure_table_exists()
        logger.info("DynamoDB table ready")
    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise e
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("APScheduler started.")
    app.state.scheduler = scheduler
    
    yield
    
    scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped.")


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


@app.post("/map-program-outcomes")
async def map_program_outcomes(request: OutcomeMappingRequest)-> dict:
    try:
        batchTranformInputBuilder = BatchTransformInputBuilder(request)
        s3_input_path = batchTranformInputBuilder.build_batch_prompt_records()
        record = lo_mapping_request_store.create_request(
            course_id=request.course_id,
            program_id=request.program_id,
            input_s3_path=s3_input_path,
            status="PENDING",
        )
        try:
            response = lambda_client.invoke(
                FunctionName="start-batch-transform-job",
                InvocationType="RequestResponse",        
                Payload=json.dumps({"record_id": record["request_id"]
                                    }).encode("utf-8")
            )

            if response["StatusCode"] != 200:
                raise HTTPException(status_code=500, detail="Lambda invocation failed")

            result = json.loads(response["Payload"].read())

            return {
                "message": result["body"]["message"],
                "jobName": result["body"]["jobName"],
                "startedForRecordId": result["body"]["startedForRecordId"],
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in mapping LOs: {e}")
        raise HTTPException(status_code=500, detail="Something went wrong while processing mapping request")
    
@app.post("/process-batch-transform-results")
async def process_batch_transform_results_endpoint(request: dict, background_tasks: BackgroundTasks) -> dict:
    # To ensure lambda_handler_process_batch_transform_inference_results does not wait for it to complete
    background_tasks.add_task(process_batch_transform_results.process_records, request["recordsAwaitingProcessing"])
    return {"message": "accepted"}

@app.post("/get-processed-results")
async def manually_trigger_processing(body: ManualProcessRequest):
    """
    Called by Laravel when it wants results for a given course_id + program_id.
 
    - Finds the latest DynamoDB record in AWAITING_COMPLETION or AWAITING_COMPLETION_FAILED status for the given course_id and program_id
    - If found: runs post-processing and returns
    - If not found: returns telling Laravel results are still being processed
    """
    logger.info(
        "Manually trigger processing request — course_id=%s program_id=%s",
        body.course_id, body.program_id,
    )
 
    record = lo_mapping_request_store.find_latest_awaiting_record_by_ids(body.course_id, body.program_id)
 
    if not record:
        # Either still pending, processing or record doesn't exist
        logger.info(
            "No AWAITING_COMPLETION or AWAITING_COMPLETION_FAILED record found for course_id=%s program=%s — still processing.",
            body.course_id, body.program,
        )
        return {
            "status": "pending",
            "message": "Results are still being processed. Please try again later.",
        }
 
    record_id = record.get("request_id")
    record_status = record.get("status")
    logger.info(
        "Found record '%s' with status '%s' — starting post-processing.",
        record_id, record_status,
    )
 
    await process_records([record])
 
    return {
        "status": "ok",
        "message": f"Results for course '{body.course_id}' / program '{body.program}' processed and sent.",
        "record_id": record_id,
    }
    
