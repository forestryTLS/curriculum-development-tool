import json
import pytest
import copy


from app.services.process_batch_transform_results import (
    parse_s3_uri,
    parse_composite_id,
    extract_generated_text,
    strip_think_tag,
    extract_label_and_explanation,
    process_jsonl_lines,
)

def _valid_payload(clo_id="10", plo_id="20") -> dict:
    return {
        "id":                     f"clo-{clo_id}__plo-{plo_id}",
        "CLO":                    "Understand systems",
        "Accreditation_Standard": "ABET",
        "is_mapped":              True,
        "explanation":            "Strong match",
        "mapLabels":              ["a", "b"],
    }


def _make_line(payload: dict, wrap_in_list=False) -> dict | list:
    line = {"generated_text": json.dumps(payload)}
    return [line] if wrap_in_list else line


def _make_line_with_think(payload: dict) -> dict:
    payload_copy = copy.deepcopy(payload)
    payload_copy["reasoning"] = "This is a test explanation that includes reasoning"
    return {"generated_text": f"{json.dumps(payload_copy)}</think>{json.dumps(payload)}"}


def _jsonl_body(*payloads) -> bytes:
    """Encode one or more payloads as a JSONL file body."""
    lines = [json.dumps({"generated_text": json.dumps(p)}) for p in payloads]
    return "\n".join(lines).encode("utf-8")


def _put_jsonl(s3_client, key: str, *payloads) -> str:
    """Upload a JSONL file to the mock S3 bucket and return its S3 URI."""
    s3_client.put_object(Bucket=TEST_BUCKET, Key=key, Body=_jsonl_body(*payloads))
    return f"s3://{TEST_BUCKET}/{key}"

class TestParseS3Uri:
    def test_valid_uri(self):
        bucket, key = parse_s3_uri("s3://my-bucket/path/to/file.jsonl")
        assert bucket == "my-bucket"
        assert key    == "path/to/file.jsonl"

    def test_uri_with_no_key(self):
        bucket, key = parse_s3_uri("s3://my-bucket/")
        assert bucket == "my-bucket"
        assert key    == ""

    def test_nested_path(self):
        bucket, key = parse_s3_uri("s3://my-bucket/a/b/c/output.jsonl")
        assert key == "a/b/c/output.jsonl"
        assert bucket == "my-bucket"

    def test_invalid_uri_raises(self):
        with pytest.raises(ValueError, match="Invalid S3 URI"):
            parse_s3_uri("https://not-s3.com/file.jsonl")

    def test_missing_scheme_raises(self):
        with pytest.raises(ValueError):
            parse_s3_uri("my-bucket/path/file.jsonl")

class TestParseCompositeId:
    def test_standard_ids(self):
        assert parse_composite_id("clo-42__plo-99") == ("42", "99")

    def test_alphanumeric_ids(self):
        clo_id, plo_id = parse_composite_id("clo-abc123__plo-xyz789")
        assert clo_id == "abc123"
        assert plo_id == "xyz789"

    def test_plo_id_with_hyphens(self):
        clo_id, plo_id = parse_composite_id("clo-1__plo-some-complex-id")
        assert clo_id == "1"
        assert plo_id == "some-complex-id"
        
    def test_invalid_format_returns_none_tuple(self):
        assert parse_composite_id("not-a-valid-id") == (None, None)

    def test_empty_string_returns_none_tuple(self):
        assert parse_composite_id("") == (None, None)

    def test_none_returns_none_tuple(self):
        assert parse_composite_id(None) == (None, None)

    def test_partial_format_returns_none_tuple(self):
        assert parse_composite_id("clo-42") == (None, None)


class TestExtractGeneratedText:
    def test_plain_dict(self):
        assert extract_generated_text({"generated_text": "hello"}) == "hello"

    def test_list_wrapped_dict(self):
        assert extract_generated_text([{"generated_text": "hello"}]) == "hello"

    def test_missing_key_returns_none(self):
        assert extract_generated_text({"other": "value"}) is None

    def test_empty_list_returns_none(self):
        assert extract_generated_text([]) is None

    def test_string_input_returns_none(self):
        assert extract_generated_text("raw string") is None

    def test_none_input_returns_none(self):
        assert extract_generated_text(None) is None

    def test_list_takes_first_item(self):
        line = [{"generated_text": "first"}, {"generated_text": "second"}]
        assert extract_generated_text(line) == "first"

class TestStripThinkTag:
    def test_strips_think_block(self):
        assert strip_think_tag("<think>reasoning</think>answer") == "answer"

    def test_strips_think_block_with_object_in_second(self):
        assert strip_think_tag("reasoning</think>{'generated_text': '{'id': test, 'clo': test}'}") == "{'generated_text': '{'id': test, 'clo': test}'}"
        
    def test_no_think_tag_unchanged(self):
        assert strip_think_tag("plain output") == "plain output"

    def test_multiline_think_block(self):
        text = "\nline one\nline two\n</think>\nreal answer"
        assert strip_think_tag(text) == "real answer"

    def test_whitespace_trimmed_after_tag(self):
        assert strip_think_tag("</think>   \n  answer") == "answer"

    def test_empty_string(self):
        assert strip_think_tag("") == ""

class TestExtractLabelAndExplanation:

    def test_full_json_response(self):
        result = extract_label_and_explanation(json.dumps(_valid_payload()))
        assert result["id"]                     == "clo-10__plo-20"
        assert result["CLO"]                    == "Understand systems"
        assert result["Accreditation_Standard"] == "ABET"
        assert result["is_mapped"]              is True
        assert result["explanation"]            == "Strong match"
        assert result["map_labels"]             == ["a", "b"]

    def test_json_missing_optional_fields_uses_defaults(self):
        result = extract_label_and_explanation(json.dumps({"id": "clo-1__plo-2"}))
        assert result["id"]                     == "clo-1__plo-2"
        assert result["CLO"]                    == ""
        assert result["Accreditation_Standard"] == ""
        assert result["is_mapped"]              is False
        assert result["map_labels"]             == []

    def test_freetext_fallback(self):
        text = (
            "id: clo-7__plo-8\n"
            "CLO: Apply knowledge\n"
            "Accreditation_Standard: ISO 9001\n"
            "explanation: Matches because of scope\n"
        )
        result = extract_label_and_explanation(text)
        assert result["id"]                     == "clo-7__plo-8"
        assert result["CLO"]                    == "Apply knowledge"
        assert result["Accreditation_Standard"] == "ISO 9001"
        assert result["explanation"]            == "Matches because of scope"
        assert result["map_labels"]             == []

    def test_freetext_unrecognised_text_returns_nones(self):
        result = extract_label_and_explanation("unrecognised text")
        assert result["id"]          is None
        assert result["explanation"] is None
        assert result["CLO"]         == ""
        assert result["Accreditation_Standard"] == ""
        assert result["map_labels"] == []
        assert result["is_mapped"]  is False

    def test_invalid_json_falls_back_without_raising(self):
        result = extract_label_and_explanation("{not valid json}")
        assert result["id"]          is None
        assert result["explanation"] is None
        assert result["CLO"]         == ""
        assert result["Accreditation_Standard"] == ""
        assert result["map_labels"] == []
        assert result["is_mapped"]  is False

class TestProcessJsonlLines:
    def test_single_valid_line(self):
        results = process_jsonl_lines([_make_line(_valid_payload())])
        assert len(results) == 1
        assert results[0]["clo_id"]    == "10"
        assert results[0]["plo_id"]    == "20"
        assert results[0]["is_mapped"] is True
        assert results[0]["map_labels"] == ["a", "b"]
        assert results[0]["explanation"]  == "Strong match"
        assert results[0]["CLO"]                    == "Understand systems"
        assert results[0]["Accreditation_Standard"] == "ABET"

    def test_think_tag_to_be_removed_before_parsing(self):
        results = process_jsonl_lines([_make_line_with_think(_valid_payload())])
        assert len(results) == 1
        assert results[0]["clo_id"]    == "10"
        assert results[0]["plo_id"]    == "20"
        assert results[0]["is_mapped"] is True
        assert results[0]["map_labels"] == ["a", "b"]
        assert results[0]["explanation"]  == "Strong match"
        assert results[0]["CLO"]                    == "Understand systems"
        assert results[0]["Accreditation_Standard"] == "ABET"

    def test_list_wrapped_line(self):
        results = process_jsonl_lines([_make_line(_valid_payload(), wrap_in_list=True)])
        assert len(results) == 1
        assert results[0]["clo_id"]    == "10"
        assert results[0]["plo_id"]    == "20"
        assert results[0]["is_mapped"] is True
        assert results[0]["map_labels"] == ["a", "b"]
        assert results[0]["explanation"]  == "Strong match"
        assert results[0]["CLO"]                    == "Understand systems"
        assert results[0]["Accreditation_Standard"] == "ABET"

    def test_line_missing_generated_text_is_skipped(self):
        assert process_jsonl_lines([{"other_key": "no text"}]) == []

    def test_invalid_composite_id_is_skipped(self):
        payload = _valid_payload()
        payload["id"] = "bad-format"
        assert process_jsonl_lines([_make_line(payload)]) == []

    def test_missing_id_is_skipped(self):
        payload = _valid_payload()
        del payload["id"]
        assert process_jsonl_lines([_make_line(payload)]) == []

    def test_multiple_valid_lines(self):
        lines = [
            _make_line(_valid_payload("1", "2")),
            _make_line(_valid_payload("3", "4")),
            _make_line(_valid_payload("5", "6")),
        ]
        results = process_jsonl_lines(lines)
        assert len(results) == 3
        assert results[0]["clo_id"] == "1"
        assert results[1]["clo_id"] == "3"
        assert results[2]["clo_id"] == "5"
        assert results[0]["plo_id"] == "2"
        assert results[1]["plo_id"] == "4"
        assert results[2]["plo_id"] == "6"
        
        #check one of them in detail to ensure parsing is correct
        assert results[0]["is_mapped"] is True
        assert results[0]["map_labels"] == ["a", "b"]
        assert results[0]["explanation"]  == "Strong match"
        assert results[0]["CLO"]                    == "Understand systems"
        assert results[0]["Accreditation_Standard"] == "ABET"

    def test_mixed_valid_and_invalid_lines(self):
        invalid_payload = _valid_payload()
        invalid_payload["id"] = "invalid-format"
        lines = [
            _make_line(_valid_payload("7", "8")),
            _make_line(invalid_payload),
            {"no_generated_text": True},
            _make_line(_valid_payload("9", "10")),
        ]
        results = process_jsonl_lines(lines)
        assert len(results) == 2
        assert results[0]["clo_id"] == "7"
        assert results[1]["clo_id"] == "9"
        assert results[0]["plo_id"] == "8"
        assert results[1]["plo_id"] == "10"
        
        #check one of them in detail to ensure parsing is correct
        assert results[0]["is_mapped"] is True
        assert results[0]["map_labels"] == ["a", "b"]
        assert results[0]["explanation"]  == "Strong match"
        assert results[0]["CLO"]                    == "Understand systems"
        assert results[0]["Accreditation_Standard"] == "ABET"
        

    def test_empty_input(self):
        assert process_jsonl_lines([]) == []