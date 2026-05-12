@extends('layouts.app')

@section('content')
<div>
    @include('courses.wizard.header')
    <div id="app">
        <div class="home">

            <div class="card" style="position:static">
                <div class="card-header wizard" >
                    <h3>
                        Course Topics
                        <div style="float: right;">
                            <button id="courseTopicsHelp" style="border: none; background: none; outline: none;" data-bs-toggle="modal" href="#guideModal">
                                <i class="bi bi-question-circle" style="color:#002145;"></i>
                            </button>
                        </div>
                        <div class="text-left">
                            @include('layouts.guide')
                        </div>
                    </h3>
                </div>

                <!-- start of add topics modal -->
                <div id="addCourseTopicsModal" class="modal fade" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" role="dialog" aria-labelledby="addCourseTopicsModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg modal-dialog-scrollable modal-dialog-centered" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="addCourseTopicsModalLabel"><i class="bi bi-pencil-fill btn-icon mr-2"></i> Course Topics</h5>
                            </div>

                            <div class="modal-body">
                                <form id="addCourseTopicsForm" class="needs-validation" novalidate>
                                    <div class="row justify-content-between align-items-end m-2">
                                        <div class="col-10">
                                            <label for="courseTopic" class="form-label fs-6"><b>Course Topic</b></label>
                                            <input id="courseTopic" class="form-control" oninput="validateMaxlength()" onpaste="validateMaxlength()" maxlength="191" placeholder="Type to search or add your own..." required>
                                            <div class="invalid-tooltip">
                                                Please provide a Course Topic.
                                            </div>                                            
                                        </div>
                                        <div class="col-2">
                                            <button id="addCourseTopicBtn" type="submit" class="btn btn-primary col">Add</button>
                                        </div>
                                    </div>
                                </form>
                                <div class="row justify-content-center">
                                    <div class="col-8">
                                        <hr>
                                    </div>
                                </div> 
                                <div class="row m-1">
                                    <table id="addCourseTopicsTbl" class="table table-light table-borderless">
                                        <thead>
                                            <tr class="table-primary">
                                                <th>Course Topic</th>
                                                <th class="text-center">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            @foreach($courseTopics as $index => $courseTopic)
                                            <tr>
                                                <td>
                                                    <input id="courseTopic{{$courseTopic->course_topic_id}}" type="text" class="form-control" oninput="validateMaxlength()" onpaste="validateMaxlength()" maxlength="191"
                                                    name="current_topics[{{$courseTopic->course_topic_id}}]" value = "{{$courseTopic->topic}}" placeholder="Type your course topic" form="saveCourseTopicChanges" required spellcheck="true" style="white-space: pre">
                                                </td>
                                                <td class="text-center">
                                                    <i class="bi bi-x-circle-fill text-danger fs-4 btn" onclick="deleteCourseTopic(this)"></i>
                                                </td>
                                            </tr>
                                            @endforeach                                               
                                        </tbody>
                                    </table>                                    
                                </div>
                            </div>
                            <form method="POST" id="saveCourseTopicChanges" action="{{ action([\App\Http\Controllers\CourseTopicController::class, 'store']) }}">
                                @csrf
                                <div class="modal-footer">
                                    <input type="hidden" name="course_id" value="{{$course->course_id}}" form="saveCourseTopicChanges">
                                    <button id="cancel" type="button" class="btn btn-secondary col-3" data-bs-dismiss="modal">Cancel</button>
                                    <button type="submit" class="btn btn-success btn col-3">Save Changes</button>
                                </div>
                            </form>    
                        </div>
                    </div>
                </div>
                <!-- End of add course topics modal -->

                <div class="card-body">
                    <div class="alert alert-primary d-flex align-items-center" role="alert" style="text-align:justify">
                        <i class="bi bi-info-circle-fill pr-2 fs-3"></i>
                        <div class="col mb-6">
                            Input the major topics covered in the course individually. These may come from the course schedule, weekly modules, lecture topics, units, or course calendar.
                        </div>
                    </div>
                <div class="row">
                    <div class="col mb-1">
                        <button type="button" class="btn btn-primary col-3 float-right bg-primary text-white fs-5" data-bs-toggle="modal" data-bs-target="#addCourseTopicsModal">
                            <i class="bi bi-plus mr-2"></i>Course Topics
                        </button>
                    </div>
                </div>


                <div id="admins">
                    <table class="table table-light" id="course_topic_table">
                        <tr class="table-primary">
                            <th>Course Topics</th>
                            <th class="text-center w-25">Actions</th>
                        </tr>

                        @if(count($courseTopics) < 1)
                            <tr>
                                <td colspan="2">
                                    <div class="alert alert-warning wizard">
                                        <i class="bi bi-exclamation-circle-fill"></i>There are no course topics set for this course.
                                    </div>
                                </td>
                            </tr>
                        @else
                            @foreach($courseTopics as $index => $courseTopic)
                                <tr>
                                    <td>
                                        {{$courseTopic->topic}}
                                    </td>
                                    <td class="text-center align-middle">
                                        <button type="button" style="width:60px;" class="btn btn-secondary btn-sm m-1" data-bs-toggle="modal" data-bs-target="#addCourseTopicsModal">
                                            Edit
                                        </button>
                                    </td>
                                </tr>
                            @endforeach
                        @endif
                    </table>
                </div>
            </div>


                <!-- card footer -->
                <div class="card-footer">
                    <div class="card-body mb-4">
                        <a href="{{route('courseWizard.step8', $course->course_id)}}">
                            <button class="btn btn-sm btn-primary col-3 float-left"><i class="bi bi-arrow-left mr-2"></i> Course Description</button>
                        </a>
                        <a href="{{route('courseWizard.step1', $course->course_id)}}">
                            <button class="btn btn-sm btn-primary col-3 float-right">Course Learning Outcomes <i class="bi bi-arrow-right ml-2"></i></button>
                        </a>
                    </div>
                </div>            
            </div>
        </div>
   </div>
</div>

<script>
    $(document).ready(function () {

    //   $("form").submit(function () {
    //     // prevent duplicate form submissions
    //     $(this).find(":submit").attr('disabled', 'disabled');
    //     $(this).find(":submit").html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');

    //   });

        $('#addCourseTopicsForm').submit(function (event) {
            // prevent default form submission handling
            event.preventDefault();
            event.stopPropagation();
            // check if input fields contain data
            if ($('#courseTopic').val().length != 0) {
                addCourseTopic();
                // reset form 
                $(this).trigger('reset');
                $(this).removeClass('was-validated');
            } else {
                // mark form as validated
                $(this).addClass('was-validated');
            }
            // readjust modal's position 
            document.querySelector('#addCourseTopicsModal').handleUpdate();

        });

        $('#cancel').click(function(event) {
            $('#addCourseTopicsTbl tbody').html(`
                @foreach($courseTopics as $index => $courseTopic)
                    <tr>
                        <td>
                            <input id="courseTopic{{$courseTopic->course_topic_id}}" type="text" class="form-control" name="current_topics[{{$courseTopic->course_topic_id}}]" value = "{{$courseTopic->topic}}" placeholder="Type your course topic" form="saveCourseTopicChanges" required spellcheck="true" style="white-space: pre">
                        </td>
                        <td class="text-center">
                            <i class="bi bi-x-circle-fill text-danger fs-4 btn" onclick="deleteCourseTopic(this)"></i>
                        </td>
                    </tr>
                @endforeach                                               
            `);
        });
    });

    function deleteCourseTopic(submitter) {
        $(submitter).parents('tr').remove();
    }

    function addCourseTopic() {
        // prepend assessment method to the table
        $('#addCourseTopicsTbl tbody').append(`
            <tr>
                <td>
                    <input type="text" class="form-control" name="new_topics[]" value = "${$('#courseTopic').val()}" placeholder="Type your course topics" form="saveCourseTopicChanges" required spellcheck="true" style="white-space: pre">
                </td>
                <td class="text-center">
                    <i class="bi bi-x-circle-fill text-danger fs-4 btn" onclick="deleteCourseTopic(this)"></i>
                </td>
            </tr>
        `);
    }


</script>
@endsection
