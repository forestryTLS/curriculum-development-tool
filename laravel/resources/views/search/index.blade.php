@extends('layouts.app')

@section('content')
    <style>
        .search-page-header {
            max-width: 760px;
            margin: 0 auto 1.5rem;
        }

        .search-input {
            min-height: 48px;
            font-size: 1.05rem;
        }

        .search-stats,
        .course-match-stats {
            color: #495057;
        }

        .course-match-stats {
            font-size: 0.9rem;
        }

        .search-result-match {
            margin-bottom: 0.65rem;
        }

        .search-result-match p {
            margin-bottom: 0.2rem;
        }

        .search-extra-matches summary {
            cursor: pointer;
            color: #0055b7;
            font-size: 0.9rem;
        }

        mark {
            padding: 0.1rem 0.2rem;
        }
    </style>

    <div class="search-page-header text-center">
        <h1 class="mb-3">Course Search</h1>

        <form method="GET" action="{{ route('search.index') }}">
            <div class="input-group input-group-lg">
                <input
                    type="search"
                    name="query"
                    value="{{ $searchTerm }}"
                    placeholder="Search courses"
                    class="form-control search-input"
                >

                <button type="button" class="btn btn-outline-secondary">
                    <i class="bi bi-funnel"></i> Filters
                </button>

                <button type="submit" class="btn btn-primary">Search</button>
            </div>

            @error('query')
                <div class='text-danger mt-2'>
                    {{$message}}
                </div>
            @enderror
        </form>
    </div>
    
    @if($searchTerm !== '' && $stats['courses'] > 0)
        <div class="search-stats text-center mb-4">
            <span>Courses: {{ $stats['courses'] }}</span>
            @if($stats['programs'] > 0)
                <span class="mx-2">|</span><span>Programs: {{ $stats['programs'] }}</span>
            @endif

            @if($stats['topics'] > 0)
                <span class="mx-2">|</span><span>Topics: {{ $stats['topics'] }}</span>
            @endif

            @if($stats['learning_outcomes'] > 0)
                <span class="mx-2">|</span><span>Learning Objectives: {{ $stats['learning_outcomes'] }}</span>
            @endif

            @if($stats['assessments'] > 0)
                <span class="mx-2">|</span><span>Assessments: {{ $stats['assessments'] }}</span>
            @endif

            @if($stats['descriptions'] > 0)
                <span class="mx-2">|</span><span>Descriptions: {{ $stats['descriptions'] }}</span>
            @endif

            @if($stats['materials'] > 0)
                <span class="mx-2">|</span><span>Materials: {{ $stats['materials'] }}</span>
            @endif
        </div>
    @elseif($searchTerm !== '')
        <p class="text-center">No matches found.</p>
    @endif




    @foreach($results as $result)
        
        <div class="border-bottom py-3">
            @if($result->course_match_snippet)
                <h3 class="mb-1">{!! $result->course_match_snippet !!}</h3>
            @else
                <h3 class="mb-1">{{ $result->course_code }} {{ $result->course_num }}: {{ $result->course_title }}</h3>
            @endif

            @if($result->programs->isNotEmpty())
                <div class="small mb-2">
                    <span class="text-muted">Programs:</span>
                    @foreach($result->programs as $program)
                        <a href="{{ route('programWizard.step1', $program->program_id) }}">{{ $program->program }}</a>@if(!$loop->last), @endif
                    @endforeach
                </div>
            @endif

            @if(array_sum($result->match_stats) > 0)
                <div class="course-match-stats mb-2">
                    <span>Matched in this course:</span>

                    @if($result->match_stats['topics'] > 0)
                        <span class="ms-2">Topics: {{ $result->match_stats['topics'] }}</span>
                    @endif

                    @if($result->match_stats['learning_outcomes'] > 0)
                        <span class="ms-2">Learning Objectives: {{ $result->match_stats['learning_outcomes'] }}</span>
                    @endif

                    @if($result->match_stats['assessments'] > 0)
                        <span class="ms-2">Assessments: {{ $result->match_stats['assessments'] }}</span>
                    @endif

                    @if($result->match_stats['descriptions'] > 0)
                        <span class="ms-2">Descriptions: {{ $result->match_stats['descriptions'] }}</span>
                    @endif

                    @if($result->match_stats['materials'] > 0)
                        <span class="ms-2">Materials: {{ $result->match_stats['materials'] }}</span>
                    @endif
                </div>
            @endif

            @foreach($result->matches->take(3) as $match)
                <div class="search-result-match">
                    <p class="small text-muted">Matched in: {{ $match->property }}</p>
                    <p>{!! $match->snippet !!}</p>
                </div>
            @endforeach

            @if($result->matches->count() > 3)
                <details class="search-extra-matches">
                    <summary>Show {{ $result->matches->count() - 3 }} more matches...</summary>

                    <div class="mt-2">
                        @foreach($result->matches->slice(3) as $match)
                            <div class="search-result-match">
                                <p class="small text-muted">Matched in: {{ $match->property }}</p>
                                <p>{!! $match->snippet !!}</p>
                            </div>
                        @endforeach
                    </div>
                </details>
            @endif
        </div>
    @endforeach

    @if($results->hasPages())
        <div class="mt-4 d-flex justify-content-center">
            {{ $results->links() }}
        </div>
    @endif
@endsection
