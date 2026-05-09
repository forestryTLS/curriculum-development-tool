"""
End-to-end test that simulates a SageMaker job completing for a course/program,
drives the polling endpoint, and verifies the AI-suggested mappings render on
Step 5 with the expected purple icons.

Skips:
  - The actual SageMaker run (LocalStack does not support batch transform).
  - The Lambda invocation chain (we directly create the AWAITING_COMPLETION
    DynamoDB record and place dummy output in S3).

Covers:
  - LocalStack DynamoDB + S3 read by FastAPI
  - FastAPI process_records pipeline
  - Laravel storeAiSuggestions controller
  - Postgres outcome_map_ai_suggestions writes
  - course_programs flag updates
  - Step 5 HTML response contains purple icons in the right cells
"""
import datetime as dt
import uuid
import time

import pytest
import requests
from bs4 import BeautifulSoup

from tests.e2e.conftest import (
    LARAVEL_URL,
    DYNAMO_TABLE_NAME,
    upload_dummy_sagemaker_output,
)


def _put_awaiting_completion_record(
    dynamo_table,
    course_id: int,
    program_id: int,
    output_s3_uri: str,
) -> str:
    """Inject a record that looks like SageMaker just finished successfully."""
    request_id = (
        dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4())
    )
    dynamo_table.put_item(Item={
        "request_id":         request_id,
        "course_id":          course_id,
        "program_id":         program_id,
        "status":             "AWAITING_COMPLETION",
        "input_s3_path":      "s3://e2e-fake/input.jsonl",
        "output_s3_path":     output_s3_uri,
        "transform_job_name": "e2e-fake-transform-job",
        "created_at":         dt.datetime.utcnow().isoformat(),
        "updated_at":         dt.datetime.utcnow().isoformat(),
    })
    return request_id


def test_ai_suggestions_render_on_step5(
    fastapi_service,
    seeded_course_program,
    s3_bucket,
    s3_client,
    dynamo_table,
    laravel_session,
    pg_conn,
):
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    # 1. Place dummy SageMaker output in S3
    output_uri = upload_dummy_sagemaker_output(
        s3_client,
        s3_bucket,
        f"output/e2e-test-{course_id}-{program_id}.jsonl.out",
    )

    # 2. Inject AWAITING_COMPLETION DynamoDB record pointing at that output
    request_id = _put_awaiting_completion_record(dynamo_table, course_id, program_id, output_uri)

    # 3. Drive the polling endpoint - this should pick up the record, deliver to
    #    Laravel, write rows, set the flags, and delete the DynamoDB record.
    r = laravel_session.post(
        f"{LARAVEL_URL}/courseWizard/{course_id}/{program_id}/check-ai-results",
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200, r.text

    # First poll triggers async processing in FastAPI; subsequent polls see the
    # local DB flag and report complete. Poll up to ~15s.
    completed = False
    for _ in range(15):
        r = laravel_session.post(
            f"{LARAVEL_URL}/courseWizard/{course_id}/{program_id}/check-ai-results",
            headers={"Accept": "application/json"},
        )
        if r.json().get("status") == "complete":
            completed = True
            break
        time.sleep(1)
    assert completed, "Polling never reported 'complete' within 15s"

    # 4. Verify Postgres state
    cur = pg_conn.cursor()
    cur.execute(
        "SELECT manual_map_status, ai_suggestion_status FROM course_programs "
        "WHERE course_id = %s AND program_id = %s",
        (course_id, program_id),
    )
    row = cur.fetchone()
    assert row == (True, True), f"Flags not set: {row}"

    cur.execute(
        "SELECT l_outcome_id, pl_outcome_id, map_scale_id FROM outcome_map_ai_suggestions "
        "WHERE l_outcome_id = ANY(%s) ORDER BY l_outcome_id, pl_outcome_id, map_scale_id",
        (seeded_course_program["clo_ids"],),
    )
    rows = cur.fetchall()
    cur.close()

    # Expected (matches sample_ai_output.jsonl):
    #   clo-99001 / plo-99001 / scale "I"      (mapped)
    #   clo-99001 / plo-99002 / scale N/A      (unmapped, written if N/A scale exists)
    #   clo-99002 / plo-99001 / scale "D"      (mapped)
    #   clo-99002 / plo-99002 / scale "I"      (mapped, multi)
    #   clo-99002 / plo-99002 / scale "D"      (mapped, multi)
    expected_minimum = {
        (99001, 99001, 99001),  # I
        (99002, 99001, 99002),  # D
        (99002, 99002, 99001),  # I
        (99002, 99002, 99002),  # D
    }
    actual = {tuple(r) for r in rows}
    missing = expected_minimum - actual
    assert not missing, f"Missing expected suggestion rows: {missing}. Actual: {actual}"

    # 5. Render Step 5 and check for purple icons
    page = laravel_session.get(f"{LARAVEL_URL}/courseWizard/{course_id}/step5")
    assert page.status_code == 200, f"Step 5 returned {page.status_code}"

    soup = BeautifulSoup(page.text, "html.parser")
    purple_imgs = [
        img for img in soup.find_all("img")
        if "AISuggestionPurple.png" in (img.get("src") or "")
    ]
    assert len(purple_imgs) >= 4, (
        f"Expected at least 4 purple icons (one per mapped scale), found {len(purple_imgs)}"
    )
