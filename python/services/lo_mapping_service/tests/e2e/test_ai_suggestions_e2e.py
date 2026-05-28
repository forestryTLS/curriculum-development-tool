"""
Unused

Covers:
  - LocalStack DynamoDB + S3 read by FastAPI
  - FastAPI process_records pipeline
  - Laravel storeAiSuggestions controller
  - Postgres outcome_map_ai_suggestions writes
  - course_programs flag updates
  - Step 5 HTML response contains purple icons in the right cells
Limitations:
  - Skips the actual SageMaker run (LocalStack does not support batch transform).
  - Skips the Lambda invocation chain (we directly create the AWAITING_COMPLETION
    DynamoDB record and place dummy output in S3).
"""
  
import datetime as dt
import tempfile
import uuid
import time
from pathlib import Path

import pytest
import requests
from bs4 import BeautifulSoup

from tests.e2e.conftest import (
    LARAVEL_URL,
    DYNAMO_TABLE_NAME,
    upload_dummy_sagemaker_output,
    get_csrf_token,
)


def _put_pending_record(dynamo_table, course_id: int, program_id: int) -> str:
    """Inject a record that looks like a freshly-submitted, not-yet-running request."""
    request_id = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S-") + str(uuid.uuid4())
    dynamo_table.put_item(Item={
        "request_id":      request_id,
        "course_id":       course_id,
        "program_id":      program_id,
        "status":          "PENDING",
        "input_s3_path":   "s3://e2e-fake/input.jsonl",
        "output_s3_path":  "s3://e2e-fake/output.jsonl.out",
        "created_at":      dt.datetime.utcnow().isoformat(),
        "updated_at":      dt.datetime.utcnow().isoformat(),
    })
    return request_id


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


def _drive_polling_to_complete(laravel_session, course_id, program_id, timeout_s: int = 15) -> None:
    """Poll /check-ai-results until status==complete or fail after timeout_s seconds."""
    csrf_token = get_csrf_token(laravel_session, f"{LARAVEL_URL}/home")
    headers = {"Accept": "application/json", "X-CSRF-TOKEN": csrf_token}
    url = f"{LARAVEL_URL}/courseWizard/{course_id}/{program_id}/check-ai-results"

    r = laravel_session.post(url, headers=headers)
    assert r.status_code == 200, r.text
    for _ in range(timeout_s):
        r = laravel_session.post(url, headers=headers)
        if r.json().get("status") == "complete":
            return
        time.sleep(1)
    raise AssertionError(f"Polling never reported 'complete' within {timeout_s}s")


def _trigger_ai_pipeline(s3_client, s3_bucket, dynamo_table, laravel_session,
                         course_id, program_id, fixture: str) -> None:
    """Upload fixture JSONL to S3, inject AWAITING_COMPLETION record, drive polling to complete."""
    output_uri = upload_dummy_sagemaker_output(
        s3_client, s3_bucket,
        f"output/e2e-{fixture}-{course_id}-{program_id}.jsonl.out",
        fixture=fixture,
    )
    _put_awaiting_completion_record(dynamo_table, course_id, program_id, output_uri)
    _drive_polling_to_complete(laravel_session, course_id, program_id)


def _suggestions_for_clos(pg_conn, clo_ids) -> list[tuple]:
    """Return [(l_outcome_id, pl_outcome_id, map_scale_id), ...] sorted, for given CLOs."""
    cur = pg_conn.cursor()
    cur.execute(
        "SELECT l_outcome_id, pl_outcome_id, map_scale_id FROM outcome_map_ai_suggestions "
        "WHERE l_outcome_id = ANY(%s) ORDER BY l_outcome_id, pl_outcome_id, map_scale_id",
        (clo_ids,),
    )
    rows = cur.fetchall()
    cur.close()
    return rows


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

    # POSTs need X-CSRF-TOKEN.
    csrf_token = get_csrf_token(laravel_session, f"{LARAVEL_URL}/home")
    post_headers = {"Accept": "application/json", "X-CSRF-TOKEN": csrf_token}

    # 3. Drive the polling endpoint - this should pick up the record, deliver to
    #    Laravel, write rows, set the flags, and delete the DynamoDB record.
    r = laravel_session.post(
        f"{LARAVEL_URL}/courseWizard/{course_id}/{program_id}/check-ai-results",
        headers=post_headers,
    )
    assert r.status_code == 200, r.text

    # First poll triggers async processing in FastAPI; subsequent polls see the
    # local DB flag and report complete. Poll up to ~15s.
    completed = False
    for _ in range(15):
        r = laravel_session.post(
            f"{LARAVEL_URL}/courseWizard/{course_id}/{program_id}/check-ai-results",
            headers=post_headers,
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

    # Dump rendered HTML so failed assertions below can be inspected post-mortem.
    html_dump = Path(tempfile.gettempdir()) / f"e2e-step5-{course_id}-{program_id}.html"
    html_dump.write_text(page.text, encoding="utf-8")

    def _ctx(msg: str) -> str:
        return f"{msg}\n  Final URL: {page.url}\n  HTML dump: {html_dump}"

    # Confirm we actually landed on step5 of OUR course (no silent redirect).
    assert page.url.rstrip("/").endswith(f"/courseWizard/{course_id}/step5"), \
        _ctx("Did not land on step5 of the test course")

    # Drill-down: prove each loop is producing content.
    assert "E2E Test Program" in page.text, _ctx("Program iteration produced no output")
    assert ("Test CLO 1" in page.text or "clo1" in page.text), _ctx("CLO iteration produced no output")
    assert ("Test PLO 1" in page.text or "plo1" in page.text), _ctx("PLO iteration produced no output")
    assert "AISuggestionPurple.png" in page.text, _ctx(
        "Page rendered programs/CLOs/PLOs but no AI suggestion icons at all - "
        "the aiSuggestedOutcomeMap relation isn't matching the seeded rows."
    )

    soup = BeautifulSoup(page.text, "html.parser")
    purple_imgs = [
        img for img in soup.find_all("img")
        if "AISuggestionPurple.png" in (img.get("src") or "")
    ]
    assert len(purple_imgs) >= 4, _ctx(
        f"Expected at least 4 purple icons (one per mapped scale), found {len(purple_imgs)}"
    )


def test_malformed_jsonl_lines_are_skipped(
    fastapi_service, seeded_course_program, s3_bucket, s3_client, dynamo_table, laravel_session, pg_conn,
):
    """Malformed JSONL lines should be skipped; valid lines should still produce rows."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    _trigger_ai_pipeline(
        s3_client, s3_bucket, dynamo_table, laravel_session,
        course_id, program_id, "malformed_ai_output.jsonl",
    )

    rows = set(_suggestions_for_clos(pg_conn, seeded_course_program["clo_ids"]))
    # malformed_ai_output.jsonl has 2 valid lines: clo-99001/plo-99001/I and clo-99002/plo-99001/D.
    assert (99001, 99001, 99001) in rows, f"Valid 'I' line missing. Got: {rows}"
    assert (99002, 99001, 99002) in rows, f"Valid 'D' line missing. Got: {rows}"
    # The 4 malformed lines should produce nothing.
    assert len(rows) == 2, f"Malformed lines produced extra rows: {rows}"


def test_unknown_scale_abbreviation_is_skipped(
    fastapi_service, seeded_course_program, s3_bucket, s3_client, dynamo_table, laravel_session, pg_conn,
):
    """Labels not in the program's mapping scales should be skipped; valid ones should still write."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    _trigger_ai_pipeline(
        s3_client, s3_bucket, dynamo_table, laravel_session,
        course_id, program_id, "unknown_scale_ai_output.jsonl",
    )

    rows = set(_suggestions_for_clos(pg_conn, seeded_course_program["clo_ids"]))
    # Fixture: clo-99001/plo-99001 has only 'P' (unknown) -> 0 rows.
    #          clo-99002/plo-99001 has 'D' -> 1 row at scale 99002.
    #          clo-99002/plo-99002 has 'I' (valid) and 'Q' (unknown) -> 1 row at scale 99001.
    assert (99002, 99001, 99002) in rows
    assert (99002, 99002, 99001) in rows
    assert not any(r[0] == 99001 and r[1] == 99001 for r in rows), \
        f"clo-99001/plo-99001 had only an unknown label; expected 0 rows. Got: {rows}"
    assert all(r[2] in {99001, 99002} for r in rows), \
        f"All scale_ids must be from the program's seeded scales. Got: {rows}"


def test_idempotent_delivery_no_duplicate_rows(
    fastapi_service, seeded_course_program, s3_bucket, s3_client, dynamo_table, laravel_session, pg_conn,
):
    """Re-delivering the same payload via the API must not duplicate outcome_map_ai_suggestions rows."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    _trigger_ai_pipeline(
        s3_client, s3_bucket, dynamo_table, laravel_session,
        course_id, program_id, "sample_ai_output.jsonl",
    )
    rows_before = sorted(_suggestions_for_clos(pg_conn, seeded_course_program["clo_ids"]))
    assert len(rows_before) > 0, "First delivery wrote no rows; cannot validate idempotency"

    # Replay the same payload directly to Laravel (bypasses FastAPI dedup; tests Laravel-side idempotency).
    payload = {
        "request_id": "e2e-replay",
        "course_id":  course_id,
        "program_id": program_id,
        "status":     "AWAITING_COMPLETION",
        "results": [
            {"clo_id": 99001, "plo_id": 99001, "is_mapped": True,  "map_labels": ["I"]},
            {"clo_id": 99001, "plo_id": 99002, "is_mapped": False, "map_labels": []},
            {"clo_id": 99002, "plo_id": 99001, "is_mapped": True,  "map_labels": ["D"]},
            {"clo_id": 99002, "plo_id": 99002, "is_mapped": True,  "map_labels": ["I", "D"]},
        ],
    }
    r = requests.post(
        f"{LARAVEL_URL}/api/microservices/lo-mapping/ai-suggestions/store",
        json=payload, timeout=10,
    )
    assert r.status_code == 200, r.text

    rows_after = sorted(_suggestions_for_clos(pg_conn, seeded_course_program["clo_ids"]))
    assert rows_after == rows_before, (
        f"Replay produced extra/different rows.\nBefore: {rows_before}\nAfter:  {rows_after}"
    )


def test_categorized_plos_render_with_icons(
    fastapi_service, seeded_course_program, s3_bucket, s3_client, dynamo_table, laravel_session, pg_conn,
):
    """The categorized-PLO branch of step5.blade.php should render purple icons too."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]
    CATEGORY_ID = 99001
    CATEGORY_LABEL = "E2E Test Category"

    cur = pg_conn.cursor()
    try:
        cur.execute(
            "INSERT INTO p_l_o_categories (plo_category_id, program_id, plo_category, created_at, updated_at) "
            "VALUES (%s, %s, %s, NOW(), NOW())",
            (CATEGORY_ID, program_id, CATEGORY_LABEL),
        )
        # Assign PLO 99001 to the category; leave 99002 uncategorized so both branches render.
        cur.execute(
            "UPDATE program_learning_outcomes SET plo_category_id = %s WHERE pl_outcome_id = 99001",
            (CATEGORY_ID,),
        )
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        cur.close()

    _trigger_ai_pipeline(
        s3_client, s3_bucket, dynamo_table, laravel_session,
        course_id, program_id, "sample_ai_output.jsonl",
    )

    page = laravel_session.get(f"{LARAVEL_URL}/courseWizard/{course_id}/step5")
    assert page.status_code == 200
    assert CATEGORY_LABEL in page.text, "Categorized branch never rendered the category"
    assert "Uncategorized PLOs" in page.text, "Uncategorized section is missing"
    assert "AISuggestionPurple.png" in page.text, "No purple icons rendered for the categorized PLO"
    # PLO 99001 is in the seeded fixture's mapped results, so its row should include at least one icon.
    soup = BeautifulSoup(page.text, "html.parser")
    purple_imgs = [img for img in soup.find_all("img") if "AISuggestionPurple.png" in (img.get("src") or "")]
    assert len(purple_imgs) >= 1, f"Expected at least one purple icon, found {len(purple_imgs)}"


def test_all_unmapped_routes_to_na_scale(
    fastapi_service, seeded_course_program, s3_bucket, s3_client, dynamo_table, laravel_session, pg_conn,
):
    """When is_mapped is false for every entry, all rows route to the pre-seeded N/A scale (id=0)."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    _trigger_ai_pipeline(
        s3_client, s3_bucket, dynamo_table, laravel_session,
        course_id, program_id, "all_unmapped_ai_output.jsonl",
    )

    rows = _suggestions_for_clos(pg_conn, seeded_course_program["clo_ids"])
    assert len(rows) == 4, f"Expected 4 rows (one per CLO/PLO pair), got {len(rows)}: {rows}"
    assert all(r[2] == 0 for r in rows), \
        f"All rows should route to N/A scale (map_scale_id=0). Got: {rows}"


LATE_CLO_ID = 99003


def _insert_late_clo(pg_conn, course_id):
    cur = pg_conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO learning_outcomes (l_outcome_id, course_id, l_outcome, clo_shortphrase, created_at, updated_at)
            VALUES (%s, %s, 'Late-added CLO', 'late', NOW(), NOW())
            ON CONFLICT (l_outcome_id) DO NOTHING
            """,
            (LATE_CLO_ID, course_id),
        )
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        cur.close()


def _delete_late_clo(pg_conn):
    cur = pg_conn.cursor()
    cur.execute("DELETE FROM outcome_map_ai_suggestions WHERE l_outcome_id = %s", (LATE_CLO_ID,))
    cur.execute("DELETE FROM outcome_maps WHERE l_outcome_id = %s", (LATE_CLO_ID,))
    cur.execute("DELETE FROM learning_outcomes WHERE l_outcome_id = %s", (LATE_CLO_ID,))
    pg_conn.commit()
    cur.close()


def _assert_late_clo_has_no_icons(pg_conn, laravel_session, course_id, program_id):
    cur = pg_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM outcome_map_ai_suggestions WHERE l_outcome_id = %s", (LATE_CLO_ID,))
    row_count = cur.fetchone()[0]
    cur.close()
    assert row_count == 0, f"Late-added CLO should have no suggestion rows; found {row_count}"

    page = laravel_session.get(f"{LARAVEL_URL}/courseWizard/{course_id}/step5")
    assert page.status_code == 200

    soup = BeautifulSoup(page.text, "html.parser")
    accordion = soup.find("div", id=f"accordionGroup{program_id}-{LATE_CLO_ID}")
    assert accordion is not None, f"Step 5 should still render the late CLO accordion ({LATE_CLO_ID})"

    purple = [
        img for img in accordion.find_all("img")
        if "AISuggestionPurple.png" in (img.get("src") or "")
    ]
    assert len(purple) == 0, f"Late-added CLO should have no purple icons; found {len(purple)}"


def test_clo_added_after_results_processed_has_no_icons(
    fastapi_service, seeded_course_program, s3_bucket, s3_client, dynamo_table, laravel_session, pg_conn,
):
    """CLO added after the AI pipeline has fully completed -> no purple icons for the new CLO."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    _trigger_ai_pipeline(
        s3_client, s3_bucket, dynamo_table, laravel_session,
        course_id, program_id, "sample_ai_output.jsonl",
    )
    _insert_late_clo(pg_conn, course_id)

    try:
        _assert_late_clo_has_no_icons(pg_conn, laravel_session, course_id, program_id)
    finally:
        _delete_late_clo(pg_conn)


def test_clo_added_while_request_in_flight_has_no_icons(
    fastapi_service, seeded_course_program, s3_bucket, s3_client, dynamo_table, laravel_session, pg_conn,
):
    """CLO added after the request was submitted but before results are processed -> still no purple icons."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    output_uri = upload_dummy_sagemaker_output(
        s3_client, s3_bucket,
        f"output/e2e-late-clo-inflight-{course_id}-{program_id}.jsonl.out",
        fixture="sample_ai_output.jsonl",
    )
    _put_awaiting_completion_record(dynamo_table, course_id, program_id, output_uri)

    _insert_late_clo(pg_conn, course_id)

    try:
        _drive_polling_to_complete(laravel_session, course_id, program_id)
        _assert_late_clo_has_no_icons(pg_conn, laravel_session, course_id, program_id)
    finally:
        _delete_late_clo(pg_conn)


def test_check_in_flight_returns_true_when_pending_record_exists(
    fastapi_service, seeded_course_program, dynamo_table, laravel_session,
):
    """Pre-click guard: Laravel's /check-in-flight should report in_flight=true when a PENDING record exists."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    _put_pending_record(dynamo_table, course_id, program_id)

    csrf_token = get_csrf_token(laravel_session, f"{LARAVEL_URL}/home")
    r = laravel_session.post(
        f"{LARAVEL_URL}/courseWizard/{course_id}/{program_id}/check-in-flight",
        headers={"Accept": "application/json", "X-CSRF-TOKEN": csrf_token},
    )
    assert r.status_code == 200, r.text
    assert r.json().get("in_flight") is True


def test_step5_renders_waiting_state_when_request_in_flight(
    fastapi_service, seeded_course_program, dynamo_table, laravel_session,
):
    """Server-side rendering: any user opening Step 5 mid-request should see Waiting + auto-poll attrs."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    _put_pending_record(dynamo_table, course_id, program_id)

    page = laravel_session.get(f"{LARAVEL_URL}/courseWizard/{course_id}/step5")
    assert page.status_code == 200

    soup = BeautifulSoup(page.text, "html.parser")

    ai_btn = soup.find(id=f"buttonAISuggestionCenter-{course_id}-{program_id}")
    assert ai_btn is not None
    assert "d-none" in (ai_btn.get("class") or []), \
        "AI Suggestion button should be hidden while a request is in flight"

    waiting_btn = soup.find(id=f"aiCheckingCenter-{course_id}-{program_id}")
    assert waiting_btn is not None
    assert "d-none" not in (waiting_btn.get("class") or []), \
        "Waiting button should be visible while a request is in flight"

    mapping_options = soup.find(id=f"mappingOptions-{course_id}-{program_id}")
    assert mapping_options is not None
    assert mapping_options.get("data-poll-on-load") == "true", \
        "mappingOptions div should carry data-poll-on-load so JS auto-resumes polling on page load"
    assert mapping_options.get("data-course-id") == str(course_id)
    assert mapping_options.get("data-program-id") == str(program_id)


def test_fastapi_dedupe_skips_creating_duplicate_record(
    fastapi_service, seeded_course_program, dynamo_table,
):
    """FastAPI /map-program-outcomes should detect an existing in-flight record and return deduplicated=true."""
    course_id  = seeded_course_program["course_id"]
    program_id = seeded_course_program["program_id"]

    existing_id = _put_pending_record(dynamo_table, course_id, program_id)

    payload = {
        "course_id":  course_id,
        "program_id": program_id,
        "course_learning_outcomes": [{"l_outcome_id": 99001, "l_outcome": "Test CLO 1"}],
        "program_learning_outcomes": [{"pl_outcome_id": 99001, "pl_outcome": "Test PLO 1"}],
        "mapping_scales": [
            {"map_scale_id": 99001, "title": "Introduced", "abbreviation": "I", "description": "Intro"},
        ],
    }

    r = requests.post(f"{fastapi_service}/map-program-outcomes", json=payload, timeout=10)
    assert r.status_code == 200, r.text

    data = r.json()
    assert data.get("deduplicated") is True, f"Expected deduplicated=true, got: {data}"
    assert data.get("startedForRecordId") == existing_id, \
        f"Dedup response should reuse the existing record id ({existing_id}), got: {data.get('startedForRecordId')}"

    item_count = dynamo_table.scan()["Count"]
    assert item_count == 1, \
        f"Dedup should not create a new DynamoDB record; expected 1 item, found {item_count}"
