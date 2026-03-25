from pydantic import BaseModel, Field 

class CourseSyllabiFile(BaseModel):
    file_path: str = Field(description="Path to the syllabi file")
    client_original_filename: str = Field(description="Original filename from the client")