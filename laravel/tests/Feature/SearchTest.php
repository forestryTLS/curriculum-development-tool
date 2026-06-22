<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\DatabaseTransactions;
use Illuminate\Foundation\Testing\WithFaker;
use Tests\TestCase;
use App\Models\AssessmentMethod;
use App\Models\Course;
use App\Models\CourseMaterial;
use App\Models\CourseTopic;
use App\Models\LearningOutcome;
use Illuminate\Support\Facades\DB;

class SearchTest extends TestCase
{
    use DatabaseTransactions;

    /**
     * A basic feature test example.
     */
    public function test_example(): void
    {
        $response = $this->get('/');

        $response->assertStatus(200);
    }

    public function test_search_page_loads_without_query(){
        $response = $this->get(route('search.index'));
        $response->assertStatus(200);
        $response->assertSee('Course Search');
    }

    public function test_search_page_displays_query(){
        $response = $this->get(route('search.index', [
            'query' => 'climate change'
        ]));

        $response->assertStatus(200);
        $response->assertSee('climate change');
    }

    public function test_search_query_whitespace_gone(){
        $response = $this->get(route('search.index', [
            'query' => '   climate        change        '
        ]));

        $response->assertStatus(200);
        $response->assertSee('climate change');
    }

    public function test_oversized_search_query(){
        $response = $this->from(route('search.index'))->get(route('search.index', [
            'query' => str_repeat('a', 201),
        ]));

        $response->assertRedirect(route('search.index'));
        $response->assertSessionHasErrors('query');
    }

    public function test_empty_search_query_allowed(){
        $response = $this->get(route('search.index', [
            'query' => '',
        ]));

        $response->assertStatus(200);
        $response->assertSessionHasNoErrors();
    }

    public function test_search_finds_course_by_compact_course_code(){
        $this->createCourseScaleCategory();

        Course::factory()->create([
            'course_code' => 'CONS',
            'course_num' => 123,
            'course_title' => 'Compact Code Match Course',
        ]);

        $response = $this->get(route('search.index', [
            'query' => 'CONS123',
        ]));

        $response->assertStatus(200);
        $response->assertSee('Compact Code Match Course');
        $response->assertSee('<mark>CONS</mark>', false);
        $response->assertDontSee('Matched in: course');
    }

    public function test_search_finds_course_by_course_title(){
        $this->createCourseScaleCategory();

        Course::factory()->create([
            'course_code' => 'FRST',
            'course_num' => 321,
            'course_title' => 'Auralith Forest Policy',
        ]);

        $response = $this->get(route('search.index', [
            'query' => 'auralith',
        ]));

        $response->assertStatus(200);
        $response->assertSee('Forest Policy');
        $response->assertSee('<mark>Auralith</mark>', false);
        $response->assertDontSee('Matched in: course');
    }

    public function test_direct_course_matches_appear_before_content_only_matches(){
        $this->createCourseScaleCategory();

        Course::factory()->create([
            'course_code' => 'CONS',
            'course_num' => 123,
            'course_title' => 'Actual Course Match',
        ]);

        $contentOnlyCourse = Course::factory()->create([
            'course_code' => 'FRST',
            'course_num' => 456,
            'course_title' => 'Description Mention Course',
        ]);

        DB::table('course_description')->insert([
            'course_id' => $contentOnlyCourse->course_id,
            'description' => 'This course references CONS123 as a related prerequisite example.',
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $response = $this->get(route('search.index', [
            'query' => 'CONS123',
        ]));

        $response->assertStatus(200);
        $response->assertSeeInOrder([
            'Actual Course Match',
            'Description Mention Course',
        ]);
        $response->assertSee('Matched in: description');
    }

    // This method creates the missing parent rows needed by the test courses.
    // updateOrInsert keeps it safe if the local database already has seeded data.
    private function createCourseScaleCategory(): void
    {
        DB::table('standard_categories')->updateOrInsert(
            ['standard_category_id' => 1],
            ['sc_name' => 'Test Standard Category']
        );

        DB::table('standards_scale_categories')->updateOrInsert(
            ['scale_category_id' => 1],
            ['name' => 'Test Scale Category']
        );
    }


    //Search Topics Querying tests
    public function test_search_finds_course_by_topic(){
        $this->createCourseScaleCategory();

        $course = Course::factory()->create([
            'course_code' => 'TEST',
            'course_num' => 101,
            'course_title' => 'Test Course',
        ]);

        CourseTopic::factory()->create([
            'course_id' => $course->course_id,
            'topic' => 'Climate change adaptaion of something something'
        ]);

        $response = $this->get(route('search.index', [
            'query' => 'climate change',
        ]));

        $response->assertStatus(200);
        $response->assertSee('TEST');
        $response->assertSee('101');
        $response->assertSee('Test Course');
    }

    public function test_search_does_not_show_course_when_topic_does_not_match(){
    $this->createCourseScaleCategory();

    $course = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 101,
        'course_title' => 'Test Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $course->course_id,
        'topic' => 'Forest ecology and biodiversity',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'climate change',
    ]));

    $response->assertStatus(200);
    $response->assertDontSee('Test Course');
}

public function test_search_only_returns_course_with_matching_topic()
{
    $this->createCourseScaleCategory();

    $matchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 101,
        'course_title' => 'Matching Course',
    ]);

    $nonMatchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 202,
        'course_title' => 'Non Matching Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $matchingCourse->course_id,
        'topic' => 'Climate change adaptation strategies',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $nonMatchingCourse->course_id,
        'topic' => 'Forest inventory and timber supply',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'climate change',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Matching Course');
    $response->assertDontSee('Non Matching Course');
}

public function test_search_returns_multiple_matching_topics_for_same_course()
{
    $this->createCourseScaleCategory();

    $course = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 101,
        'course_title' => 'Climate Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $course->course_id,
        'topic' => 'Climate change adaptation strategies',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $course->course_id,
        'topic' => 'Climate change impacts on forests',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $course->course_id,
        'topic' => 'Soil classification methods',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'climate change',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Climate Course');
    $response->assertSee('adaptation strategies');
    $response->assertSee('impacts on forests');
    $response->assertDontSee('Soil classification methods');
}

public function test_search_finds_course_by_description()
{
    $this->createCourseScaleCategory();

    $course = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 303,
        'course_title' => 'Description Match Course',
    ]);

    DB::table('course_description')->insert([
        'course_id' => $course->course_id,
        'description' => 'This course studies zirconium watershed planning and applied environmental analysis.',
        'created_at' => now(),
        'updated_at' => now(),
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'zirconium',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Description Match Course');
    $response->assertSee('Matched in: description');
    $response->assertSee('zirconium', false);
}

public function test_search_only_returns_course_with_matching_learning_objective()
{
    $this->createCourseScaleCategory();

    $matchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 606,
        'course_title' => 'Learning Objective Match Course',
    ]);

    $nonMatchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 607,
        'course_title' => 'Learning Objective Non Match Course',
    ]);

    LearningOutcome::create([
        'course_id' => $matchingCourse->course_id,
        'l_outcome' => 'Evaluate aurorium restoration planning in urban landscapes.',
        'clo_shortphrase' => 'Evaluate aurorium restoration',
    ]);

    LearningOutcome::create([
        'course_id' => $nonMatchingCourse->course_id,
        'l_outcome' => 'Explain forest inventory sampling methods.',
        'clo_shortphrase' => 'Explain sampling',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'aurorium',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Learning Objective Match Course');
    $response->assertSee('Matched in: learning outcome');
    $response->assertSee('aurorium', false);
    $response->assertDontSee('Learning Objective Non Match Course');
}

public function test_search_only_returns_course_with_matching_description()
{
    $this->createCourseScaleCategory();

    $matchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 707,
        'course_title' => 'Description Only Match Course',
    ]);

    $nonMatchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 708,
        'course_title' => 'Description Non Match Course',
    ]);

    DB::table('course_description')->insert([
        [
            'course_id' => $matchingCourse->course_id,
            'description' => 'This course introduces solandria watershed governance and planning.',
            'created_at' => now(),
            'updated_at' => now(),
        ],
        [
            'course_id' => $nonMatchingCourse->course_id,
            'description' => 'This course introduces silviculture and forest operations.',
            'created_at' => now(),
            'updated_at' => now(),
        ],
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'solandria',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Description Only Match Course');
    $response->assertSee('Matched in: description');
    $response->assertSee('solandria', false);
    $response->assertDontSee('Description Non Match Course');
}

public function test_search_finds_course_by_material()
{
    $this->createCourseScaleCategory();

    $course = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 404,
        'course_title' => 'Material Match Course',
    ]);

    CourseMaterial::factory()->create([
        'course_id' => $course->course_id,
        'name' => 'Nebulagraph field guide',
        'type' => 'textbook',
        'description' => 'Required material for applied field methods',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'nebulagraph',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Material Match Course');
    $response->assertSee('Matched in: material');
    $response->assertSee('nebulagraph', false);
}

public function test_search_only_returns_course_with_matching_material()
{
    $this->createCourseScaleCategory();

    $matchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 808,
        'course_title' => 'Material Only Match Course',
    ]);

    $nonMatchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 809,
        'course_title' => 'Material Non Match Course',
    ]);

    CourseMaterial::factory()->create([
        'course_id' => $matchingCourse->course_id,
        'name' => 'Velorium case study collection',
        'type' => 'article',
        'description' => 'Recommended readings for environmental policy.',
    ]);

    CourseMaterial::factory()->create([
        'course_id' => $nonMatchingCourse->course_id,
        'name' => 'Forest measurements handbook',
        'type' => 'textbook',
        'description' => 'Required field methods reference.',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'velorium',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Material Only Match Course');
    $response->assertSee('Matched in: material');
    $response->assertSee('velorium', false);
    $response->assertDontSee('Material Non Match Course');
}

public function test_search_finds_course_by_assessment()
{
    $this->createCourseScaleCategory();

    $course = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 505,
        'course_title' => 'Assessment Match Course',
    ]);

    AssessmentMethod::create([
        'course_id' => $course->course_id,
        'a_method' => 'Capstone xenolith analysis presentation',
        'weight' => 35,
        'pos_in_alignment' => 0,
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'xenolith',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Assessment Match Course');
    $response->assertSee('Matched in: assessment');
    $response->assertSee('xenolith', false);
}

public function test_search_only_returns_course_with_matching_assessment()
{
    $this->createCourseScaleCategory();

    $matchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 909,
        'course_title' => 'Assessment Only Match Course',
    ]);

    $nonMatchingCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 910,
        'course_title' => 'Assessment Non Match Course',
    ]);

    AssessmentMethod::create([
        'course_id' => $matchingCourse->course_id,
        'a_method' => 'Mycelion policy memo and oral presentation',
        'weight' => 25,
        'pos_in_alignment' => 0,
    ]);

    AssessmentMethod::create([
        'course_id' => $nonMatchingCourse->course_id,
        'a_method' => 'Final exam and weekly participation',
        'weight' => 40,
        'pos_in_alignment' => 0,
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'mycelion',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Assessment Only Match Course');
    $response->assertSee('Matched in: assessment');
    $response->assertSee('mycelion', false);
    $response->assertDontSee('Assessment Non Match Course');
}

public function test_topic_match_ranks_above_material_match()
{
    $this->createCourseScaleCategory();

    $topicCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 111,
        'course_title' => 'Topic Match Course',
    ]);

    $materialCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 222,
        'course_title' => 'Material Match Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $topicCourse->course_id,
        'topic' => 'Zenthos climate adaptation',
    ]);

    CourseMaterial::factory()->create([
        'course_id' => $materialCourse->course_id,
        'name' => 'Zenthos climate adaptation reading',
        'type' => 'article',
        'description' => 'Required material',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'zenthos',
    ]));

    $response->assertStatus(200);
    $response->assertSeeInOrder([
        'Topic Match Course',
        'Material Match Course',
    ]);
}

public function test_multiple_lower_weight_matches_can_outrank_single_topic_match()
{
    $this->createCourseScaleCategory();

    $topicCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 333,
        'course_title' => 'Single Topic Course',
    ]);

    $materialCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 444,
        'course_title' => 'Multiple Material Matches Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $topicCourse->course_id,
        'topic' => 'Vorlan sustainability systems',
    ]);

    for ($index = 0; $index < 6; $index++) {
        CourseMaterial::factory()->create([
            'course_id' => $materialCourse->course_id,
            'name' => "Vorlan reading package {$index}",
            'type' => 'article',
            'description' => 'Recommended material',
        ]);
    }

    $response = $this->get(route('search.index', [
        'query' => 'vorlan',
    ]));

    $response->assertStatus(200);
    $response->assertSeeInOrder([
        'Multiple Material Matches Course',
        'Single Topic Course',
    ]);
}

public function test_direct_course_match_ranks_above_higher_content_score()
{
    $this->createCourseScaleCategory();

    Course::factory()->create([
        'course_code' => 'CONS',
        'course_num' => 123,
        'course_title' => 'Direct Course Match',
    ]);

    $contentCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 555,
        'course_title' => 'High Content Match Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $contentCourse->course_id,
        'topic' => 'CONS123 policy topic',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $contentCourse->course_id,
        'topic' => 'CONS123 advanced topic',
    ]);

    CourseMaterial::factory()->create([
        'course_id' => $contentCourse->course_id,
        'name' => 'CONS123 reading package',
        'type' => 'article',
        'description' => 'Required reading',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'CONS123',
    ]));

    $response->assertStatus(200);
    $response->assertSeeInOrder([
        'Direct Course Match',
        'High Content Match Course',
    ]);
}

public function test_search_stats_show_total_matches_by_property()
{
    $this->createCourseScaleCategory();

    $course = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 111,
        'course_title' => 'Stats Match Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $course->course_id,
        'topic' => 'Glacier adaptation topic one',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $course->course_id,
        'topic' => 'Glacier adaptation topic two',
    ]);

    LearningOutcome::create([
        'course_id' => $course->course_id,
        'l_outcome' => 'Explain glacier adaptation planning.',
        'clo_shortphrase' => 'Explain glacier adaptation',
    ]);

    AssessmentMethod::create([
        'course_id' => $course->course_id,
        'a_method' => 'Glacier adaptation presentation',
        'weight' => 25,
        'pos_in_alignment' => 0,
    ]);

    DB::table('course_description')->insert([
        'course_id' => $course->course_id,
        'description' => 'This course covers glacier adaptation examples.',
        'created_at' => now(),
        'updated_at' => now(),
    ]);

    CourseMaterial::factory()->create([
        'course_id' => $course->course_id,
        'name' => 'Glacier adaptation reading',
        'type' => 'article',
        'description' => 'Required material',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'glacier adaptation',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Courses: 1');
    $response->assertSee('Topics: 2');
    $response->assertSee('Learning Objectives: 1');
    $response->assertSee('Assessments: 1');
    $response->assertSee('Descriptions: 1');
    $response->assertSee('Materials: 1');
}

public function test_search_stats_count_distinct_courses_and_total_topic_matches()
{
    $this->createCourseScaleCategory();

    $firstCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 222,
        'course_title' => 'First Stats Course',
    ]);

    $secondCourse = Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 333,
        'course_title' => 'Second Stats Course',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $firstCourse->course_id,
        'topic' => 'Hydrology climate topic one',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $firstCourse->course_id,
        'topic' => 'Hydrology climate topic two',
    ]);

    CourseTopic::factory()->create([
        'course_id' => $secondCourse->course_id,
        'topic' => 'Hydrology climate topic three',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'hydrology climate',
    ]));

    $response->assertStatus(200);
    $response->assertSee('Courses: 2');
    $response->assertSee('Topics: 3');
    $response->assertDontSee('Learning Objectives:');
    $response->assertDontSee('Assessments:');
    $response->assertDontSee('Descriptions:');
    $response->assertDontSee('Materials:');
}

public function test_search_stats_show_zero_when_query_has_no_results()
{
    $this->createCourseScaleCategory();

    Course::factory()->create([
        'course_code' => 'TEST',
        'course_num' => 444,
        'course_title' => 'No Match Course',
    ]);

    $response = $this->get(route('search.index', [
        'query' => 'nonexistentsearchterm',
    ]));

    $response->assertStatus(200);
    $response->assertSee('No matches found.');
    $response->assertDontSee('Courses: 0');
    $response->assertDontSee('Topics: 0');
    $response->assertDontSee('Learning Objectives: 0');
    $response->assertDontSee('Assessments: 0');
    $response->assertDontSee('Descriptions: 0');
    $response->assertDontSee('Materials: 0');
}
    
}
