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
    




    @foreach ($results as $result)
        <p>
            {{ $result->course_code }} {{ $result->course_num }}:
            {{ $result->course_title }}
        </p>

        <p>Matched in: {{ $result->property }}</p>
        <p>{!! $result->snippet !!}</p>
    @endforeach
@endsection