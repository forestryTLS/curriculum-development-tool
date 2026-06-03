<?php

it('shows the AI Suggestions button on step 5 when a course is linked to a program with PLOs', function () {
    $user = makeTestUser('e2e-step5@ubc.ca');
    $course = makeTestCourse('E2E Step 5 Course');
    $program = makeTestProgram('E2E Step 5 Program');

    linkUserToCourse($user, $course);
    linkCourseToProgram($course, $program);
    attachMappingScalesToProgram($program);

    addCloToCourse($course, 'CLO 1: Apply concepts');
    addCloToCourse($course, 'CLO 2: Analyze problems');
    addPloToProgram($program, 'PLO 1: Demonstrate mastery');
    addPloToProgram($program, 'PLO 2: Communicate effectively');

    $this->actingAs($user);

    $page = visit("/courseWizard/{$course->course_id}/step5");

    $page->assertNoJavascriptErrors();
    $page->click("[data-bs-target=\"#collapseProgramAccordion{$program->program_id}\"]");
    $page->assertSee('AI Suggestions');
});
