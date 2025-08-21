@component('mail::message')


# Courses Created From Uploaded Syllabi Files

Hello {{ $userName }},

{{$successfulCreations}} course(s) were successfully created from the uploaded syllabi files. {{$unsuccessfulCreations}} file(s) failed to process. Please log in to review the created courses.


@component('mail::button', ['url' => config('app.login_url')])
Log In and Review Courses
@endcomponent
<br>
{{ config('app.name') }}
@endcomponent
