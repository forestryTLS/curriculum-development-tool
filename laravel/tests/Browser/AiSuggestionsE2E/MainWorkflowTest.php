<?php

use App\Models\Course;
use App\Models\LearningOutcome;
use App\Models\Program;
use App\Models\ProgramLearningOutcome;

/**
 * Tests main workflow without 'complications'
 * Tests that mapping works when CLO has categories
 */
it('creates a course and program via the UI and renders AI suggestion icons end-to-end', function () {
    $user = makeTestUser('e2e-normal-workflow@ubc.ca');
    $this->actingAs($user);

    // Create course
    $page = visit('/home');
    $page->click('[data-bs-target="#methodToCreateNewCourse"]')
        ->click('[data-bs-target="#createCourseModal"]')
        ->type('#course_code', 'HAPP')
        ->type('#course_num', '101')
        ->type('#course_title', 'E2E Normal workflow Course')
        ->select('#course_semester', 'W1')
        ->select('#course_year', '2026')
        ->select('#delivery_modality', 'O')
        ->select('#standard_category_id', '1')
        ->click('#createCourse #submit'); // POSTs and redirects to /courseWizard/{id}/step8

    $course = Course::where('course_title', 'E2E Normal workflow Course')->latest('course_id')->firstOrFail();

    // Add CLO
    $page->click('a[href$="/courseWizard/' . $course->course_id . '/step1"]')
        ->click('[data-bs-target="#addLearningOutcomeModal"]')
        ->type('#l_outcome', 'Students apply core concepts to novel problems.')
        ->type('#title', 'Apply Concepts')
        ->click('#addCLOBtn')                            // append row
        ->click('#saveCLOChanges button[type="submit"]'); // persist

    $clo = LearningOutcome::where('course_id', $course->course_id)->firstOrFail();

    // Create program
    $page->click('a[href$="/home"]')
        ->click('[data-bs-target="#createProgramModal"]')
        ->type('#program', 'E2E Normal workflow Program')
        ->check('input[name="level"][value="Bachelors"]')
        ->click('#createProgramModal button[type="submit"]'); // redirects to /programWizard/{id}/step1

    $program = Program::where('program', 'E2E Normal workflow Program')->latest('program_id')->firstOrFail();

    // Add 3 PLOs
    $page->click('[data-bs-target="#addPLOModal"]')
        ->type('#pl_outcome', 'PLO 1: Demonstrate mastery of the discipline.')
        ->type('#ploShortphrase', 'Demonstrate Mastery')
        ->click('#addPLOBtn')
        ->type('#pl_outcome', 'PLO 2: Synthesize ideas across domains.')
        ->type('#ploShortphrase', 'Synthesize Ideas')
        ->click('#addPLOBtn')
        ->type('#pl_outcome', 'PLO 3: Evaluate competing approaches.')
        ->type('#ploShortphrase', 'Evaluate Approaches')
        ->click('#addPLOBtn')
        ->click('#savePLOChanges button[type="submit"]');

    // These also function as assertions that the PLOs were stored correctly in the db
    $plo1 = ProgramLearningOutcome::where('pl_outcome', 'PLO 1: Demonstrate mastery of the discipline.')->firstOrFail();
    $plo2 = ProgramLearningOutcome::where('pl_outcome', 'PLO 2: Synthesize ideas across domains.')->firstOrFail();
    $plo3 = ProgramLearningOutcome::where('pl_outcome', 'PLO 3: Evaluate competing approaches.')->firstOrFail();

    // Assign default I/D/A mapping scales to the program
    $page->click('a[href$="/programWizard/' . $program->program_id . '/step2"]')
        ->click('[data-bs-target=".mapping-scales"]')
        ->click('form[action*="addDefaultMappingScale"]:has(input[name="mapping_scale_categories_id"][value="1"]) button[type="submit"]');

    // Map the course to the program
    $page->click('a[href$="/programWizard/' . $program->program_id . '/step3"]')
        ->click('[data-bs-target="#addCourseModal"]')
        ->check('input[name="selectedCourses[]"][value="' . $course->course_id . '"]')
        ->click('button[form="addExistCourse"]');

    // If we submit the job via UI, it will fail because that calls the lambda that invokes SageMaker
    // So instead, we directly create the pending record and write Mock SageMaker output
    putPendingRecord($course->course_id, $program->program_id);
    // The mock mappings we set here don't directly
    setAwaitingCompletion($course->course_id, $program->program_id, [
        ['clo_id' => $clo->l_outcome_id, 'plo_id' => $plo1->pl_outcome_id, 'labels' => ['I']],      // single map
        ['clo_id' => $clo->l_outcome_id, 'plo_id' => $plo2->pl_outcome_id, 'labels' => []],         // no map, should show as N/A
        ['clo_id' => $clo->l_outcome_id, 'plo_id' => $plo3->pl_outcome_id, 'labels' => ['I', 'D']], // multi map
    ]);

    // Reload the page. Now that we have a record awaiting completion, it should auto-poll and
    // FastAPI should get the results from LocalStack, and send them to Laravel
    $page->refresh();
    // $page->navigate("/courseWizard/{$course->course_id}/step5");

    // Scale values: I, D, A, N/A
    $I = 1;
    $D = 2;
    $A = 3;
    $NA = 0;

    $page->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo1->pl_outcome_id, $I))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo1->pl_outcome_id, $D))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo1->pl_outcome_id, $A))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo1->pl_outcome_id, $NA));

    $page->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo2->pl_outcome_id, $NA))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo2->pl_outcome_id, $D))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo2->pl_outcome_id, $A))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo2->pl_outcome_id, $I));

    $page->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo3->pl_outcome_id, $I))
        ->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo3->pl_outcome_id, $D))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo3->pl_outcome_id, $A))
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo3->pl_outcome_id, $NA));

    // 8. The icons rendered, so the polling-driven delivery has run: verify the
    //    underlying rows + flag the pipeline wrote (single map, N/A, multi map).
    $this->assertDatabaseHas('course_programs', [
        'course_id' => $course->course_id,
        'program_id' => $program->program_id,
        'ai_suggestion_status' => true,
    ]);
    $this->assertDatabaseHas('outcome_map_ai_suggestions', [
        'l_outcome_id' => $clo->l_outcome_id,
        'pl_outcome_id' => $plo1->pl_outcome_id,
        'map_scale_id' => $I, // 'I'
    ]);
    $this->assertDatabaseHas('outcome_map_ai_suggestions', [
        'l_outcome_id' => $clo->l_outcome_id,
        'pl_outcome_id' => $plo2->pl_outcome_id,
        'map_scale_id' => $NA, // N/A
    ]);
    $this->assertDatabaseHas('outcome_map_ai_suggestions', [
        'l_outcome_id' => $clo->l_outcome_id,
        'pl_outcome_id' => $plo3->pl_outcome_id,
        'map_scale_id' => $I, // multi 'I'
    ]);
    $this->assertDatabaseHas('outcome_map_ai_suggestions', [
        'l_outcome_id' => $clo->l_outcome_id,
        'pl_outcome_id' => $plo3->pl_outcome_id,
        'map_scale_id' => $D, // multi 'D'
    ]);

    // Add manual maps over the AI suggestions, one that matches the AI and one that doesn't
    $page->click(programAccordionToggle($program->program_id))
        ->click(cloAccordionToggle($program->program_id, $clo->l_outcome_id))
        ->check(manualMapField($clo->l_outcome_id, $plo1->pl_outcome_id), (string) $I)
        ->check(manualMapField($clo->l_outcome_id, $plo3->pl_outcome_id), (string) $A)
        ->click('Save');

    // Check checkboxes reflect the manual choices; the purple icons still reflect the AI suggestions
    $page->refresh();
    $page->assertPresent(manualMapCheckbox($clo->l_outcome_id, $plo1->pl_outcome_id, $I) . ':checked')
        ->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo1->pl_outcome_id, $I))            // manual + AI on I
        ->assertPresent(manualMapCheckbox($clo->l_outcome_id, $plo3->pl_outcome_id, $A) . ':checked')
        ->assertMissing(aiIconForCloPlo($clo->l_outcome_id, $plo3->pl_outcome_id, $A))            // manual A, no AI on A
        ->assertMissing(manualMapCheckbox($clo->l_outcome_id, $plo3->pl_outcome_id, $I) . ':checked')
        ->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo3->pl_outcome_id, $I))            // AI on I still there
        ->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo3->pl_outcome_id, $D))            // AI on D still there
        ->assertPresent(aiIconForCloPlo($clo->l_outcome_id, $plo2->pl_outcome_id, $NA));          // PLO 2 AI N/A untouched

    $this->assertDatabaseHas('outcome_maps', [
        'l_outcome_id' => $clo->l_outcome_id,
        'pl_outcome_id' => $plo1->pl_outcome_id,
        'map_scale_id' => $I,
    ]);
    $this->assertDatabaseHas('outcome_maps', [
        'l_outcome_id' => $clo->l_outcome_id,
        'pl_outcome_id' => $plo3->pl_outcome_id,
        'map_scale_id' => $A,
    ]);
});
