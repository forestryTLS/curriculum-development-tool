<?php

it('renders waiting state after the user clicks AI Suggestions and confirms', function () {
    $user = makeTestUser('e2e-pending@ubc.ca');
    $course = makeTestCourse('E2E Pending Course');
    $program = makeTestProgram('E2E Pending Program');

    linkUserToCourse($user, $course);
    linkCourseToProgram($course, $program);
    attachMappingScalesToProgram($program);

    addCloToCourse($course, 'CLO 1: Apply concepts');
    addPloToProgram($program, 'PLO 1: Demonstrate mastery');

    $this->actingAs($user);

    $page = visit("/courseWizard/{$course->course_id}/step5");
    $page->click("[data-bs-target=\"#collapseProgramAccordion{$program->program_id}\"]");
    $page->click("#buttonAISuggestionCenter-{$course->course_id}-{$program->program_id}");

    $yesButtonSelector = "#AiSuggestionConfirmation{$course->course_id}{$program->program_id} .btn-success";
    $page->click($yesButtonSelector);

    // $page->assertSee('Submitting');
    // $page->assertAttribute($yesButtonSelector, 'disabled', 'true');

    markRecordInProgress($course->course_id, $program->program_id);

    // $page->script("hideAiModal({$course->course_id}, {$program->program_id})");

    $page = visit("/courseWizard/{$course->course_id}/step5");
    $page->click("[data-bs-target=\"#collapseProgramAccordion{$program->program_id}\"]");
    $page->assertSee('Waiting for AI suggestions...');

    // $page->pause();
});
