from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import syllabus_parser

app = FastAPI()

class CourseSyllabiFile(BaseModel):
    file_path: str
    client_original_filename: str

@app.post("/create_course_from_syllabi")
async def create_course_from_syllabi(request: CourseSyllabiFile):
    try:
        # print("Received request to create course from syllabi file")
        result = syllabus_parser.get_course_from_text_file(request.file_path, request.client_original_filename)
        response = {"status": "success", "data": result, "message": "Course created successfully"}
        # print("Result from syllabus_parser:", result)
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    config = uvicorn.Config(app, host="127.0.0.1", port=8001)
    server = uvicorn.Server(config)
    server.run()