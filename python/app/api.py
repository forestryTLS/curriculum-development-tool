from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models import CourseSyllabiFile
import app.syllabus_parser as syllabus_parser
from app.utils.logging_config import logger  

app = FastAPI(
    title="Curriculum Development Tool Python API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/create_course_from_syllabi")
async def create_course_from_syllabi(request: CourseSyllabiFile):
    try:
        # print("Received request to create course from syllabi file")
        result = syllabus_parser.get_course_from_text_file(request.file_path, request.client_original_filename)
        response = {"status": "success", "data": result, "message": "Course created successfully"}
        # print("Result from syllabus_parser:", result)
        return response
    except Exception as e:
        logger.error(f"Error in create_course_from_syllabi: {e}")
        return {"status": "error", "message": "An error occurred while processing the request."}
