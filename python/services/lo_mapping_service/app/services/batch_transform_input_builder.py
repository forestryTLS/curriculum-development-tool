import json
import os
from datetime import datetime

from app.schemas import (
    CourseLearningOutcome,
    MappingScaleOption,
    OutcomeMappingRequest,
    ProgramLearningOutcome,
)


class BatchTransformInputBuilder:
    """Builds batch transform input JSONL files for CLO-PLO mapping."""

    def __init__(self, request: OutcomeMappingRequest) -> None:
        self.request = request

    def build_batch_prompt_records(self) -> str:
        # Use course_id and program_id from OutcomeMappingRequest
        course_id = getattr(self.request, 'course_id', None)
        program_id = getattr(self.request, 'program_id', None)

        #if Course Id or Program Id is not present
        if course_id is None:
            course_id = 'unknowncourse'
        if program_id is None:
            program_id = 'unknownprogram'

        course_id_str = self._sanitize(course_id)
        program_id_str = self._sanitize(program_id)

        # Create a unique filename using timestamp, course and program ids
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        out_dir = os.path.join(os.path.dirname(__file__), "batch_inputs")
        os.makedirs(out_dir, exist_ok=True)
        filename = f"batch_transform_input__courseid-{course_id_str}__programid-{program_id_str}__{timestamp}.jsonl"
        file_path = os.path.join(out_dir, filename)

        with open(file_path, "w", encoding="utf-8") as f:
            for clo in self.request.course_learning_outcomes:
                for plo in self.request.program_learning_outcomes:
                    pair_id = self._build_pair_id(clo, plo)
                    prompt = self._build_prompt(clo, plo, pair_id)
                    payload = self._build_jsonl_payload(pair_id, prompt)
                    f.write(json.dumps(payload, ensure_ascii=False) + "\n")

        return file_path

    def _build_pair_id(
        self,
        clo: CourseLearningOutcome,
        plo: ProgramLearningOutcome,
    ) -> str:
        return f"clo-{clo.l_outcome_id}__plo-{plo.pl_outcome_id}"

    def _build_prompt(
        self,
        clo: CourseLearningOutcome,
        plo: ProgramLearningOutcome,
        pair_id: str,
    ) -> str:
        mapping_scales_text = self._format_mapping_scales_for_prompt(
            self.request.mapping_scales
        )

        return "\n".join(
            [
                "<|im_start|>system",
                "You are an experienced course designer who aligns Course Learning Outcomes (CLOs) with accreditation standards.",
                "You follow instructions precisely and always return responses in JSON format for given CLO and accreditation standard pair, the JSON must be the following object (not wrapped in any other key):",
                "{ ",
                '"id": <given id for CLO and accreditation standard pair>, ',
                '"CLO": "<given CLO>", ',
                '"Accreditation_Standard": "<given accreditation standard>", ',
                '"is_mapped": true or false, ',
                '"mapLabels": ["I", "R", "E"], ',
                '"explanation": "<explanation phrase>", ',
                "} ",
                "Note: A CLO may span multiple mapping scale levels. If so, classify it under all relevant levels. ",
                "<|im_end|>",
                "<|im_start|>user",
                "An instructor has developed Course Learning Outcomes (CLOs) for a course syllabus and seeks assistance in aligning each CLO with each accreditation standard and categorizing its cognitive level according to the given mapping scale. ",
                "As an experienced course designer:",
                "  1. Compare the given CLO with the given accreditation standard to determine if there is alignment.",
                "  2. If they align, give an explanation for why they align. ",
                "  3. If they align, classify the CLO into one or more levels of the given mapping scale:",
                "     Mapping Scale Levels: ",
                mapping_scales_text,
                "Please review the following CLO and accreditation standard and complete the alignment, explanation, and mapping level determination:",
                "CLO: " + clo.l_outcome,
                "Accreditation Standard: " + plo.pl_outcome,
                "id: " + pair_id,
                "<|im_end|>",
                "<|im_start|>assistant",
                "/no_think"
            ]
        )

    def _build_jsonl_payload(
        self,
        pair_id: str,
        prompt: str,
    ) -> dict[str, object]:
        return {
            "id": pair_id,
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1500, 
                "return_full_text": False, 
                "stop": ["<|im_start|>", "<|im_end|>"], 
                "enable_thinking": False
                }
        }

    def _format_mapping_scales_for_prompt(
        self, scales: list[MappingScaleOption]
    ) -> str:
        if not scales:
            return "- No mapping scales were provided."

        formatted_scales: list[str] = []
        for scale in scales:
            formatted_scales.append(f"       {scale.abbreviation} - {scale.title}")

        return "\n".join(formatted_scales)
    
    # Sanitize for filename (remove spaces, special chars)
    def _sanitize(self, val):
        return str(val).replace(' ', '_').replace('/', '_').replace('\\', '_')
