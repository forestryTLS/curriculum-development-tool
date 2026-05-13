@extends('layouts.app')

@section('content')
<div>
    @include('courses.wizard.header')
    <div id="app">
        <div class="home">

            <div class="card" style="position:static">
                <div class="card-header wizard" >
                    <h3>
                        Course Materials
                        <div style="float: right;">
                            <button id="courseMaterialsHelp" style="border: none; background: none; outline: none;" data-bs-toggle="modal" href="#guideModal">
                                <i class="bi bi-question-circle" style="color:#002145;"></i>
                            </button>
                        </div>
                        <div class="text-left">
                            @include('layouts.guide')
                        </div>
                    </h3>
                </div>

                <!-- start of add materials modal -->
                <div id="addCourseMaterialsModal" class="modal fade" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" role="dialog" aria-labelledby="addCourseMaterialsModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-xl modal-dialog-scrollable modal-dialog-centered" role="document">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title" id="addCourseMaterialsModalLabel"><i class="bi bi-pencil-fill btn-icon mr-2"></i> Course Materials</h5>
                            </div>

                            <div class="modal-body">
                                <form id="addCourseMaterialsForm" class="needs-validation" novalidate>
                                    <!-- Materials have multiple fields, so the add form collects one complete material row. -->
                                    <div class="row justify-content-between align-items-end m-2">
                                        <div class="col-4">
                                            <label for="courseMaterialName" class="form-label fs-6"><b>Name</b></label>
                                            <input id="courseMaterialName" class="form-control" oninput="validateMaxlength()" onpaste="validateMaxlength()" maxlength="191" placeholder="Material name" required>
                                            <div class="invalid-tooltip">
                                                Please provide a material name.
                                            </div>
                                        </div>
                                        <div class="col-2">
                                            <label for="courseMaterialType" class="form-label fs-6"><b>Type</b></label>
                                            <input id="courseMaterialType" class="form-control" oninput="validateMaxlength()" onpaste="validateMaxlength()" maxlength="191" placeholder="Textbook, video, article...">
                                        </div>
                                        <div class="col-2">
                                            <label for="courseMaterialUrl" class="form-label fs-6"><b>URL</b></label>
                                            <input id="courseMaterialUrl" class="form-control" placeholder="https://...">
                                        </div>
                                        <div class="col-2 text-center">
                                            <label for="courseMaterialRequired" class="form-label fs-6"><b>Required</b></label>
                                            <div class="form-check d-flex justify-content-center">
                                                <input id="courseMaterialRequired" type="checkbox" class="form-check-input" value="1">
                                            </div>
                                        </div>
                                        <div class="col-2">
                                            <button id="addCourseMaterialBtn" type="submit" class="btn btn-primary col">Add</button>
                                        </div>
                                    </div>
                                    <div class="row m-2">
                                        <div class="col">
                                            <label for="courseMaterialDescription" class="form-label fs-6"><b>Description</b></label>
                                            <textarea id="courseMaterialDescription" class="form-control" rows="2" placeholder="Brief description"></textarea>
                                        </div>
                                    </div>
                                </form>
                                <div class="row justify-content-center">
                                    <div class="col-8">
                                        <hr>
                                    </div>
                                </div>
                                <div class="row m-1">
                                    <table id="addCourseMaterialsTbl" class="table table-light table-borderless">
                                        <thead>
                                            <tr class="table-primary">
                                                <th>Name</th>
                                                <th>Type</th>
                                                <th>Description</th>
                                                <th>URL</th>
                                                <th class="text-center">Required</th>
                                                <th class="text-center">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            @foreach($courseMaterials as $index => $courseMaterial)
                                            <tr>
                                                <td>
                                                    <input id="courseMaterialName{{$courseMaterial->course_material_id}}" type="text" class="form-control" oninput="validateMaxlength()" onpaste="validateMaxlength()" maxlength="191"
                                                    name="current_material[{{$courseMaterial->course_material_id}}][name]" value="{{$courseMaterial->name}}" placeholder="Material name" form="saveCourseMaterialChanges" required spellcheck="true" style="white-space: pre">
                                                </td>
                                                <td>
                                                    <input id="courseMaterialType{{$courseMaterial->course_material_id}}" type="text" class="form-control" oninput="validateMaxlength()" onpaste="validateMaxlength()" maxlength="191"
                                                    name="current_material[{{$courseMaterial->course_material_id}}][type]" value="{{$courseMaterial->type}}" placeholder="Type" form="saveCourseMaterialChanges" spellcheck="true" style="white-space: pre">
                                                </td>
                                                <td>
                                                    <textarea id="courseMaterialDescription{{$courseMaterial->course_material_id}}" class="form-control" rows="1" name="current_material[{{$courseMaterial->course_material_id}}][description]" placeholder="Description" form="saveCourseMaterialChanges" spellcheck="true">{{$courseMaterial->description}}</textarea>
                                                </td>
                                                <td>
                                                    <input id="courseMaterialUrl{{$courseMaterial->course_material_id}}" type="text" class="form-control"
                                                    name="current_material[{{$courseMaterial->course_material_id}}][url]" value="{{$courseMaterial->url}}" placeholder="URL" form="saveCourseMaterialChanges" spellcheck="true">
                                                </td>
                                                <td class="text-center">
                                                    <input type="checkbox" class="form-check-input" name="current_material[{{$courseMaterial->course_material_id}}][is_required]" value="1" form="saveCourseMaterialChanges" @checked($courseMaterial->is_required)>
                                                </td>
                                                <td class="text-center">
                                                    <i class="bi bi-x-circle-fill text-danger fs-4 btn" onclick="deleteCourseMaterial(this)"></i>
                                                </td>
                                            </tr>
                                            @endforeach
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <!-- This form sends all current_material/new_material arrays to CourseMaterialController@store. -->
                            <form method="POST" id="saveCourseMaterialChanges" action="{{ action([\App\Http\Controllers\CourseMaterialController::class, 'store']) }}">
                                @csrf
                                <div class="modal-footer">
                                    <input type="hidden" name="course_id" value="{{$course->course_id}}" form="saveCourseMaterialChanges">
                                    <button id="cancel" type="button" class="btn btn-secondary col-3" data-bs-dismiss="modal">Cancel</button>
                                    <button type="submit" class="btn btn-success btn col-3">Save Changes</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
                <!-- End of add course materials modal -->

                <div class="card-body">
                    <div class="alert alert-primary d-flex align-items-center" role="alert" style="text-align:justify">
                        <i class="bi bi-info-circle-fill pr-2 fs-3"></i>
                        <div class="col mb-6">
                            Input the main course materials individually. These may include textbooks, articles, videos, websites, datasets, or other required and recommended resources.
                        </div>
                    </div>
                <div class="row">
                    <div class="col mb-1">
                        <button type="button" class="btn btn-primary col-3 float-right bg-primary text-white fs-5" data-bs-toggle="modal" data-bs-target="#addCourseMaterialsModal">
                            <i class="bi bi-plus mr-2"></i>Course Materials
                        </button>
                    </div>
                </div>


                <div id="admins">
                    <table class="table table-light" id="course_material_table">
                        <tr class="table-primary">
                            <th>Name</th>
                            <th>Type</th>
                            <th>Description</th>
                            <th class="text-center">Required</th>
                            <th class="text-center w-25">Actions</th>
                        </tr>

                        @if(count($courseMaterials) < 1)
                            <tr>
                                <td colspan="5">
                                    <div class="alert alert-warning wizard">
                                        <i class="bi bi-exclamation-circle-fill"></i>There are no course materials set for this course.
                                    </div>
                                </td>
                            </tr>
                        @else
                            @foreach($courseMaterials as $index => $courseMaterial)
                                <tr>
                                    <td>
                                        {{$courseMaterial->name}}
                                        @if($courseMaterial->url)
                                            <br><a href="{{$courseMaterial->url}}" target="_blank" rel="noopener noreferrer">{{$courseMaterial->url}}</a>
                                        @endif
                                    </td>
                                    <td>
                                        {{$courseMaterial->type}}
                                    </td>
                                    <td>
                                        {{$courseMaterial->description}}
                                    </td>
                                    <td class="text-center">
                                        @if($courseMaterial->is_required)
                                            Required
                                        @else
                                            Optional
                                        @endif
                                    </td>
                                    <td class="text-center align-middle">
                                        <button type="button" style="width:60px;" class="btn btn-secondary btn-sm m-1" data-bs-toggle="modal" data-bs-target="#addCourseMaterialsModal">
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
                        <a href="{{route('courseWizard.step9', $course->course_id)}}">
                            <button class="btn btn-sm btn-primary col-3 float-left"><i class="bi bi-arrow-left mr-2"></i> Course Topics</button>
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

        $('#addCourseMaterialsForm').submit(function (event) {
            // prevent default form submission handling
            event.preventDefault();
            event.stopPropagation();
            // check if input fields contain data
            if ($('#courseMaterialName').val().length != 0) {
                addCourseMaterial();
                // reset form
                $(this).trigger('reset');
                $(this).removeClass('was-validated');
            } else {
                // mark form as validated
                $(this).addClass('was-validated');
            }
            // readjust modal's position
            document.querySelector('#addCourseMaterialsModal').handleUpdate();

        });

        $('#cancel').click(function(event) {
            $('#addCourseMaterialsTbl tbody').html(`
                @foreach($courseMaterials as $index => $courseMaterial)
                    <tr>
                        <td>
                            <input id="courseMaterialName{{$courseMaterial->course_material_id}}" type="text" class="form-control" name="current_material[{{$courseMaterial->course_material_id}}][name]" value="{{$courseMaterial->name}}" placeholder="Material name" form="saveCourseMaterialChanges" required spellcheck="true" style="white-space: pre">
                        </td>
                        <td>
                            <input id="courseMaterialType{{$courseMaterial->course_material_id}}" type="text" class="form-control" name="current_material[{{$courseMaterial->course_material_id}}][type]" value="{{$courseMaterial->type}}" placeholder="Type" form="saveCourseMaterialChanges" spellcheck="true" style="white-space: pre">
                        </td>
                        <td>
                            <textarea id="courseMaterialDescription{{$courseMaterial->course_material_id}}" class="form-control" rows="1" name="current_material[{{$courseMaterial->course_material_id}}][description]" placeholder="Description" form="saveCourseMaterialChanges" spellcheck="true">{{$courseMaterial->description}}</textarea>
                        </td>
                        <td>
                            <input id="courseMaterialUrl{{$courseMaterial->course_material_id}}" type="text" class="form-control" name="current_material[{{$courseMaterial->course_material_id}}][url]" value="{{$courseMaterial->url}}" placeholder="URL" form="saveCourseMaterialChanges" spellcheck="true">
                        </td>
                        <td class="text-center">
                            <input type="checkbox" class="form-check-input" name="current_material[{{$courseMaterial->course_material_id}}][is_required]" value="1" form="saveCourseMaterialChanges" @checked($courseMaterial->is_required)>
                        </td>
                        <td class="text-center">
                            <i class="bi bi-x-circle-fill text-danger fs-4 btn" onclick="deleteCourseMaterial(this)"></i>
                        </td>
                    </tr>
                @endforeach
            `);
        });
    });

    function deleteCourseMaterial(submitter) {
        $(submitter).parents('tr').remove();
    }

    function addCourseMaterial() {
        // Build grouped request keys because each material has several fields.
        const materialIndex = $('#addCourseMaterialsTbl tbody tr').length;
        const requiredInput = $('#courseMaterialRequired').is(':checked')
            ? `<input type="checkbox" class="form-check-input" name="new_material[${materialIndex}][is_required]" value="1" form="saveCourseMaterialChanges" checked>`
            : `<input type="checkbox" class="form-check-input" name="new_material[${materialIndex}][is_required]" value="1" form="saveCourseMaterialChanges">`;

        $('#addCourseMaterialsTbl tbody').append(`
            <tr>
                <td>
                    <input type="text" class="form-control" name="new_material[${materialIndex}][name]" value="${$('#courseMaterialName').val()}" placeholder="Material name" form="saveCourseMaterialChanges" required spellcheck="true" style="white-space: pre">
                </td>
                <td>
                    <input type="text" class="form-control" name="new_material[${materialIndex}][type]" value="${$('#courseMaterialType').val()}" placeholder="Type" form="saveCourseMaterialChanges" spellcheck="true" style="white-space: pre">
                </td>
                <td>
                    <textarea class="form-control" rows="1" name="new_material[${materialIndex}][description]" placeholder="Description" form="saveCourseMaterialChanges" spellcheck="true">${$('#courseMaterialDescription').val()}</textarea>
                </td>
                <td>
                    <input type="text" class="form-control" name="new_material[${materialIndex}][url]" value="${$('#courseMaterialUrl').val()}" placeholder="URL" form="saveCourseMaterialChanges" spellcheck="true">
                </td>
                <td class="text-center">
                    ${requiredInput}
                </td>
                <td class="text-center">
                    <i class="bi bi-x-circle-fill text-danger fs-4 btn" onclick="deleteCourseMaterial(this)"></i>
                </td>
            </tr>
        `);
    }


</script>
@endsection
