from typing import List, Optional

from pydantic import BaseModel, Field


class CourseLearningOutcome(BaseModel):
    l_outcome_id: int = Field(description="Course learning outcome identifier")
    l_outcome: str = Field(description="Course learning outcome text")


class ProgramLearningOutcome(BaseModel):
    pl_outcome_id: int = Field(description="Program learning outcome identifier")
    pl_outcome: str = Field(description="Program learning outcome text")


class MappingScaleOption(BaseModel):
    map_scale_id: int = Field(description="Mapping scale identifier")
    title: str = Field(description="Mapping scale title")
    abbreviation: str = Field(description="Mapping scale abbreviation")
    description: str = Field(description="Mapping scale description")


class OutcomeMappingRequest(BaseModel):
    course_id: Optional[int] = Field(
        default=None, description="Course identifier when available"
    )
    program_id: Optional[int] = Field(
        default=None, description="Program identifier when available"
    )
    course_learning_outcomes: List[CourseLearningOutcome] = Field(
        default_factory=list,
        description="Course learning outcomes to evaluate",
    )
    program_learning_outcomes: List[ProgramLearningOutcome] = Field(
        default_factory=list,
        description="Program learning outcomes to evaluate",
    )
    mapping_scales: List[MappingScaleOption] = Field(
        default_factory=list,
        description="Allowed mapping scales for this request",
    )
