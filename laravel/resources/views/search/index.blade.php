@extends('layouts.app')

@section('content')
    <h1>Course Search</h1>

    <form method="GET" action="{{ route('search.index') }}">
        <input
            type="search"
            name="query"
            value="{{ $searchTerm }}"
            placeholder="Search courses"
        >

        <button type="submit">Search</button>

        @error('query')
            <div class='text-danger mt-2'>
                {{$message}}
            </div>
        @enderror
    </form>
    
    @if($searchTerm !== '' && $stats['courses'] > 0)
        <div>
            <p>Courses: {{ $stats['courses'] }}</p>

            @if($stats['topics'] > 0)
                <p>Topics: {{ $stats['topics'] }}</p>
            @endif

            @if($stats['learning_outcomes'] > 0)
                <p>Learning Objectives: {{ $stats['learning_outcomes'] }}</p>
            @endif

            @if($stats['assessments'] > 0)
                <p>Assessments: {{ $stats['assessments'] }}</p>
            @endif

            @if($stats['descriptions'] > 0)
                <p>Descriptions: {{ $stats['descriptions'] }}</p>
            @endif

            @if($stats['materials'] > 0)
                <p>Materials: {{ $stats['materials'] }}</p>
            @endif
        </div>
    @elseif($searchTerm !== '')
        <p>No matches found.</p>
    @endif




    @foreach($results as $result)
        
        <div>
            @if($result->course_match_snippet)
                <h3>{!! $result->course_match_snippet !!}</h3>
            @else
                <h3>{{ $result->course_code }} {{ $result->course_num }}: {{ $result->course_title }}</h3>
            @endif

            @foreach($result->matches as $match)
                <p>Matched in: {{ $match->property }}</p>
                <p>{!! $match->snippet !!}</p>
            @endforeach
        </div>
    @endforeach
@endsection
