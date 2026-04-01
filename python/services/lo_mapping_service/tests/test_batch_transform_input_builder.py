import json
import os
import pytest
from pathlib import Path

from app.schemas import (
    CourseLearningOutcome,
    MappingScaleOption,
    OutcomeMappingRequest,
    ProgramLearningOutcome,
)
from app.services.batch_transform_input_builder import BatchTransformInputBuilder


@pytest.fixture
def sample_clo():
    """Create a sample Course Learning Outcome."""
    return CourseLearningOutcome(
        l_outcome_id=1,
        l_outcome="Students will understand and apply basic programming concepts"
    )


@pytest.fixture
def sample_plo():
    """Create a sample Program Learning Outcome."""
    return ProgramLearningOutcome(
        pl_outcome_id=101,
        pl_outcome="Graduates will demonstrate competency in software engineering practices"
    )


@pytest.fixture
def sample_mapping_scale():
    """Create a sample Mapping Scale Option."""
    return MappingScaleOption(
        map_scale_id=1,
        title="Introduce",
        abbreviation="I",
        description="Fundamental understanding"
    )


@pytest.fixture
def sample_request(sample_clo, sample_plo, sample_mapping_scale):
    """Create a sample OutcomeMappingRequest."""
    return OutcomeMappingRequest(
        course_id=201,
        program_id=301,
        course_learning_outcomes=[sample_clo],
        program_learning_outcomes=[sample_plo],
        mapping_scales=[sample_mapping_scale]
    )


@pytest.fixture
def sample_request_with_multiple_outcomes():
    """Create a request with multiple CLOs and PLOs."""
    return OutcomeMappingRequest(
        course_id=202,
        program_id=302,
        course_learning_outcomes=[
            CourseLearningOutcome(l_outcome_id=1, l_outcome="Outcome 1"),
            CourseLearningOutcome(l_outcome_id=2, l_outcome="Outcome 2"),
        ],
        program_learning_outcomes=[
            ProgramLearningOutcome(pl_outcome_id=101, pl_outcome="PLO 1"),
            ProgramLearningOutcome(pl_outcome_id=102, pl_outcome="PLO 2"),
        ],
        mapping_scales=[
            MappingScaleOption(map_scale_id=1, title="MyLabel1", abbreviation="ML1", description="My description 1"),
            MappingScaleOption(map_scale_id=2, title="MyLabel2", abbreviation="ML2", description="My description 2"),
            MappingScaleOption(map_scale_id=3, title="MyLabel3", abbreviation="ML3", description="My description 3"),
        ]
    )


class TestBatchTransformInputBuilder:

    def test_build_pair_id(self, sample_clo, sample_plo, sample_request):
        builder = BatchTransformInputBuilder(sample_request)
        pair_id = builder._build_pair_id(sample_clo, sample_plo)
        
        assert pair_id == "clo-1__plo-101"

    def test_format_mapping_scales_for_prompt_with_scales(self, sample_request):
        builder = BatchTransformInputBuilder(sample_request)
        
        scales = [
            MappingScaleOption(map_scale_id=1, title="Introduce", abbreviation="I", description="Intro"),
            MappingScaleOption(map_scale_id=2, title="Reinforce", abbreviation="R", description="Reinforce"),
        ]
        
        formatted = builder._format_mapping_scales_for_prompt(scales)
        # print(formatted)
        
        assert "       I - Introduce\n       R - Reinforce" == formatted

    def test_format_mapping_scales_for_prompt_empty(self, sample_request):
        builder = BatchTransformInputBuilder(sample_request)
        
        formatted = builder._format_mapping_scales_for_prompt([])
        
        assert "No mapping scales were provided" in formatted

    def test_build_prompt(self, sample_clo, sample_plo, sample_request_with_multiple_outcomes):
        builder = BatchTransformInputBuilder(sample_request_with_multiple_outcomes)
        pair_id = "clo-1__plo-101"
        
        prompt = builder._build_prompt(sample_clo, sample_plo, pair_id)
        
        assert prompt == "<|im_start|>system\nYou are an experienced course designer who aligns Course Learning Outcomes (CLOs) with accreditation standards.\nYou follow instructions precisely and always return responses in JSON format for given CLO and accreditation standard pair, the JSON must be the following object (not wrapped in any other key):\n{ \n\"id\": <given id for CLO and accreditation standard pair>, \n\"CLO\": \"<given CLO>\", \n\"Accreditation_Standard\": \"<given accreditation standard>\", \n\"is_mapped\": true or false, \n\"mapLabels\": [\"ML1\", \"ML2\", \"ML3\"], \n\"explanation\": \"<explanation phrase>\", \n} \nNote: A CLO may span multiple mapping scale levels. If so, classify it under all relevant levels. \n<|im_end|>\n<|im_start|>user\nAn instructor has developed Course Learning Outcomes (CLOs) for a course syllabus and seeks assistance in aligning each CLO with each accreditation standard and categorizing its cognitive level according to the given mapping scale. \nAs an experienced course designer:\n  1. Compare the given CLO with the given accreditation standard to determine if there is alignment.\n  2. If they align, give an explanation for why they align. \n  3. If they align, classify the CLO into one or more levels of the given mapping scale:\n     Mapping Scale Levels: \n       ML1 - MyLabel1\n       ML2 - MyLabel2\n       ML3 - MyLabel3\nPlease review the following CLO and accreditation standard and complete the alignment, explanation, and mapping level determination:\nCLO: Students will understand and apply basic programming concepts\nAccreditation Standard: Graduates will demonstrate competency in software engineering practices\nid: clo-1__plo-101\n<|im_end|>\n<|im_start|>assistant\n/no_think"

    def test_build_jsonl_payload(self, sample_request):
        builder = BatchTransformInputBuilder(sample_request)
        
        pair_id = "clo-1__plo-101"
        prompt = "Test prompt"
        payload = builder._build_jsonl_payload(pair_id, prompt)
        
        assert payload["id"] == pair_id
        assert payload["inputs"] == prompt
        assert "parameters" in payload
        assert payload["parameters"]["max_new_tokens"] == 1500
        assert payload["parameters"]["return_full_text"] is False
        assert payload["parameters"]["enable_thinking"] is False
        assert "<|im_start|>" in payload["parameters"]["stop"]
        assert "<|im_end|>" in payload["parameters"]["stop"]

    def test_sanitize_removes_spaces(self, sample_request):
        builder = BatchTransformInputBuilder(sample_request)
        
        result = builder._sanitize("test value")
        assert result == "test_value"

    def test_sanitize_removes_slashes(self, sample_request):
        builder = BatchTransformInputBuilder(sample_request)
        
        result = builder._sanitize("test/value\\path")
        assert result == "test_value_path"
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_handles_integers(self, sample_request):
        builder = BatchTransformInputBuilder(sample_request)
        
        result = builder._sanitize(12345)
        assert result == "12345"
        
    def test_build_mapping_scale_labels_list(self, sample_request_with_multiple_outcomes):
        builder = BatchTransformInputBuilder(sample_request_with_multiple_outcomes)
        
        map_labels_json = builder._build_mapping_scale_labels_list(sample_request_with_multiple_outcomes.mapping_scales)
        
        expected_labels = ["ML1", "ML2", "ML3"]
        expected_json = json.dumps(expected_labels)
        
        assert map_labels_json == expected_json

    # Test to check if file was created and uploaded to S3, this test will download the file from S3 
    # and check if it exists and is not empty
    
    # def test_upload_to_s3(self, sample_request_with_multiple_outcomes):
    #     import boto3
        
    #     if not os.getenv("BATCH_TRANSFORM_INPUT_S3_BUCKET"):
    #         pytest.skip("BATCH_TRANSFORM_INPUT_S3_BUCKET environment variable not set")
    #     if not os.getenv("ACCESS_KEY") or not os.getenv("SECRET_KEY"):
    #         pytest.skip("AWS credentials (ACCESS_KEY, SECRET_KEY) not set")
        
    #     builder = BatchTransformInputBuilder(sample_request_with_multiple_outcomes)
        
    #     # Upload to S3 and get the S3 path
    #     s3_path = builder.build_batch_prompt_records()
        
    #     # Verify the returned path format
    #     assert s3_path.startswith("s3://")
        
    #     # Parse S3 path to extract bucket and key
    #     s3_parts = s3_path.replace("s3://", "").split("/", 1)
    #     bucket_name = s3_parts[0]
    #     s3_key = s3_parts[1]
        
    #     # Download the file from S3
    #     boto_session = boto3.Session(
    #         aws_access_key_id=os.getenv("ACCESS_KEY"),
    #         aws_secret_access_key=os.getenv("SECRET_KEY"),
    #         region_name=os.getenv("AWS_REGION")
    #     )
    #     s3_client = boto_session.client("s3")
        
    #     local_filename = s3_key.split("/")[-1]
    #     local_path = os.path.join(os.getcwd(), local_filename)
    #     s3_client.download_file(Bucket=bucket_name, Key=s3_key, Filename=local_path)
        
    #     assert os.path.exists(local_path), "Downloaded file should exist locally"
    #     assert os.path.getsize(local_path) > 0, "Downloaded file should not be empty"
        
    #     print(f"File downloaded to: {local_path}")
            
            
        
