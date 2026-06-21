<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Collection;

class SearchController extends Controller

{
    public function index(Request $request){
        $searchTerm = trim($request->input('query', ''));

        $validated = $request->validate([
            'query' => ['nullable', 'string', 'max:200'],
        ]); //a query could be missing or empty. If it exists, it must be a string. Max 200 characters long.

        $searchTerm = $validated['query'] ?? '';
        $searchTerm = trim($searchTerm);
        $searchTerm = preg_replace('/\s+/', ' ', $searchTerm); #for normalizing internal whitepace

        $results = collect();

        if($searchTerm !== ''){
            $results = $this->searchCourses($searchTerm);
        }


        return view('search.index', [
            'searchTerm' => $searchTerm,
            'results' => $results,
        ]);
}

    public function searchCourses(string $searchTerm){
        //$topicsMatches = $this->searchTopics($searchTerm);
/*      $results = collect();
        $learningObjectiveMatches = $this->searchLearningObjectives($searchTerm);
        $descriptionMatches = $this->searchDescription($searchTerm);
        $assesmentMatches = $this->searchAssesments($searchTerm);
        $learningMaterialsMatches = $this->searchLearningMaterials($searchTerm);
        $courseMatches = $this->searchCourseNames($searchTerm);

        $results = $this->reorderAndCombineResults($topicsMatches,
        $learningObjectiveMatches, 
        $descriptionMatches, 
        $assesmentMatches, 
        $learningMaterialsMatches, 
        $courseMatches);

        return $results; */

        $searchResults = collect()
            ->merge($this->searchCourseNames($searchTerm))
            ->merge($this->searchTopics($searchTerm))
            ->merge($this->searchLearningObjectives($searchTerm))
            ->merge($this->searchDescriptions($searchTerm))
            ->merge($this->searchMaterials($searchTerm))
            ->merge($this->searchAssessments($searchTerm));

        $results = $this->combineMatchesByCourse($searchResults);

        return $results;
    }

    public function searchTopics(string $searchTerm){
        $results = DB::table('course_topics')
            ->join('courses', 'courses.course_id', '=', 'course_topics.course_id')
            ->whereRaw( //need to use raw SQL to support SQL functions like to_tsvector and ts_headline
                "to_tsvector('english', course_topics.topic) @@ websearch_to_tsquery('english', ?)",
                [$searchTerm])
            ->selectRaw("
                courses.course_id,
                courses.course_code,
                courses.course_num,
                courses.course_title,
                'topic' as property,
                course_topics.topic as matched_text,
                ts_headline(
                    'english',
                    course_topics.topic,
                    websearch_to_tsquery('english', ?),
                    'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=4, MaxWords=20'
                ) as snippet
            ", [$searchTerm])->get();
            
            //add ordering, limits (dynamic), and stuff styllll
            return $results;
    }

    public function searchLearningObjectives(string $searchTerm){
        $results = DB::table('learning_outcomes')
        ->join('courses', 'courses.course_id', '=', 'learning_outcomes.course_id')
        ->whereRaw(
            "to_tsvector('english', learning_outcomes.l_outcome) @@ websearch_to_tsquery('english', ?)",
            [$searchTerm])
        ->selectRaw("
            courses.course_id,
            courses.course_code,
            courses.course_num,
            courses.course_title,
            'learning outcome' as property,
            learning_outcomes.l_outcome as matched_text,
            ts_headline(
                'english',
                learning_outcomes.l_outcome,
                websearch_to_tsquery('english', ?),
                'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=4, MaxWords=20'
            ) as snippet
        ", [$searchTerm])->get();

        return $results;
    }

    public function searchDescriptions(string $searchTerm){
        $results = DB::table('course_description')
        ->join('courses', 'courses.course_id', '=', 'course_description.course_id')
        ->whereRaw(
            "to_tsvector('english', course_description.description) @@ websearch_to_tsquery('english', ?)",
            [$searchTerm])
        ->selectRaw("
            courses.course_id,
            courses.course_code,
            courses.course_num,
            courses.course_title,
            'description' as property,
            course_description.description as matched_text,
            ts_headline(
                'english',
                course_description.description,
                websearch_to_tsquery('english', ?),
                'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=4, MaxWords=20'
            ) as snippet
        ", [$searchTerm])->get();

        return $results;
    }

    public function searchMaterials(string $searchTerm){
        $results = DB::table('course_materials')
        ->join('courses', 'courses.course_id', '=', 'course_materials.course_id')
        ->whereRaw(
            "to_tsvector('english', concat_ws(' ', course_materials.name, course_materials.type, course_materials.description)) @@ websearch_to_tsquery('english', ?)",
            [$searchTerm])
        ->selectRaw("
            courses.course_id,
            courses.course_code,
            courses.course_num,
            courses.course_title,
            'material' as property,
            concat_ws(' ', course_materials.name, course_materials.type, course_materials.description) as matched_text,
            ts_headline(
                'english',
                concat_ws(' ', course_materials.name, course_materials.type, course_materials.description),
                websearch_to_tsquery('english', ?),
                'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=4, MaxWords=20'
            ) as snippet
        ", [$searchTerm])->get();

        return $results;
    }

    public function searchAssessments(string $searchTerm){
        $results = DB::table('assessment_methods')
        ->join('courses', 'courses.course_id', '=', 'assessment_methods.course_id')
        ->whereRaw(
            "to_tsvector('english', assessment_methods.a_method) @@ websearch_to_tsquery('english', ?)",
            [$searchTerm])
        ->selectRaw("
            courses.course_id,
            courses.course_code,
            courses.course_num,
            courses.course_title,
            'assessment' as property,
            assessment_methods.a_method as matched_text,
            ts_headline(
                'english',
                assessment_methods.a_method,
                websearch_to_tsquery('english', ?),
                'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=4, MaxWords=20'
            ) as snippet
        ", [$searchTerm])->get();

        return $results;
    }

    public function searchCourseNames(string $searchTerm){
        $searchText = "concat_ws(' ', courses.course_code, courses.course_num, courses.course_title)";
        $normalizedSearchTerm = preg_replace('/^([A-Za-z]+)\s*(\d+)$/', '$1 $2', $searchTerm);

        $results = DB::table('courses')
            ->whereRaw(
                "to_tsvector('english', {$searchText}) @@ websearch_to_tsquery('english', ?)",
                [$normalizedSearchTerm]
            )
            ->selectRaw("
                courses.course_id,
                courses.course_code,
                courses.course_num,
                courses.course_title,
                'course' as property,
                {$searchText} as matched_text,
                ts_headline(
                    'english',
                    {$searchText},
                    websearch_to_tsquery('english', ?),
                    'StartSel=<mark>, StopSel=</mark>, MaxFragments=2, MinWords=4, MaxWords=20'
                ) as snippet
            ", [$normalizedSearchTerm])
            ->get();

        return $results;
    }

    public function combineMatchesByCourse(Collection $matches): Collection{

        $combinedResults = collect();

        foreach($matches as $match){
            $courseId = $match->course_id;

            if(!$combinedResults->has($courseId)){
                $combinedResults[$courseId] = (object) [
                    'course_id' => $courseId,
                    'course_code' => $match->course_code,
                    'course_num' => $match->course_num,
                    'course_title' => $match->course_title,
                    'course_match_snippet' => null,
                    'is_course_match' => false,
                    'matches' => collect(),
                ];
            }

            if($match->property === 'course'){
                $combinedResults[$courseId]->course_match_snippet = $match->snippet;
                $combinedResults[$courseId]->is_course_match = true;
                continue;
            }

            $combinedResults[$courseId]->matches->push((object) [
                'property' => $match->property,
                'matched_text' => $match->matched_text,
                'snippet' => $match->snippet,
            ]);

        }

        return $combinedResults->sortByDesc('is_course_match')->values(); //removes course_id as index for the blade view to cleanly loop through results.

    }


}
