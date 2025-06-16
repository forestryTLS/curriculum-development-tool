@extends('layouts.app')

@section('content')
<div class="container" style="display: flex;justify-content: center;">
        <div class="row" style="width:75%">
            <div class="col-md-12 col-md-offset-1">

                <div class="card mb-5 mt-5" style="background-color: white;">
                    <div class="card-header">
                        <b>Assign Role</b>
                    </div>

                    <div class="card-body">
                        <div class="form-text text-muted mb-4">
                                <p>Enter the email address and the role you would like to assign to a person.</p>
                                    <li class="mb-1 mr-4 ml-4"><strong>Admin</strong> can view, edit and manage collaborators and content for all courses and programs.</li>
                                    <li class="mb-1 mr-4 ml-4"><b>Department Head</b> can view, edit and manage collaborators and content for all courses and program within assigned department.</li>
                                    <li class="mb-3 mr-4 ml-4"><b>Program Director</b> can view, edit and manage collaborators and content for assigned program and its associated courses.</li>
                        </div>
                        <form action="{{ route('admin.assignRole') }}" method="POST">
                            @csrf
                            <div class="row m-2 position-relative">
                                <div class="col-8">
                                    <input id="" type="email" name="email" class="form-control" placeholder="john.doe@ubc.ca" aria-label="email" required>
                                    <div class="invalid-tooltip">
                                        Please provide a valid email ending with ubc.ca.
                                    </div>
                                </div>
                                <div class="col-4">
                                    <select class="form-select" id="role" name="role">
                                        <option value="admin" selected>Admin</option>
                                        <option value="department-head">Department Head</option>
                                        <option value="program-director">Program Director</option>
                                    </select>
                                </div>
                            </div>
                            <div id="campus-div" class="row m-2 position-relative" hidden>
                                <div class="col-12">
                                    <select id="campus" class="custom-select" name="campus">
                                        <option disabled selected hidden>Open list of campuses</option>
                                        @foreach ($campuses as $campus)
                                            <option value="{{$campus->campus}}">{{$campus->campus}}</option>
                                        @endforeach
{{--                                        <option value="Other">Other</option>--}}
                                    </select>
                                    <input id='campus-text' class="form-control campus_text" name="campus" type="text" placeholder="Enter the campus name" disabled hidden></input>
                                    @error('campus')
                                    <span class="invalid-feedback" role="alert">
                                        <strong>{{ $message }}</strong>
                                    </span>
                                    @enderror
                                </div>
                            </div>
                            <div id="faculty-div" class="row m-2 position-relative" hidden>
                                <div class="col-12">
                                    <select id="faculty" class="custom-select" name="faculty" disabled>
                                        <option disabled selected hidden>Open list of faculties/schools</option>
                                    </select>
                                    <input id='faculty-text' class="form-control faculty_text" name="faculty" type="text" placeholder="Enter the faculty/school" disabled hidden></input>
                                    @error('faculty')
                                    <span class="invalid-feedback" role="alert">
                                        <strong>{{ $message }}</strong>
                                    </span>
                                    @enderror
                                </div>
                            </div>
                            <div id="department-div" class="row m-2 position-relative" hidden>
                                <div class="col-12">
                                    <select id="department" class="custom-select department_select" name="department" disabled>
                                        <option disabled selected hidden>Open list of departments</option>
                                    </select>
                                    <input id='department-text' class="form-control" name="department" type="text" placeholder="Enter the department" disabled hidden></input>
                                     @error('department')
                                    <span class="invalid-feedback" role="alert">
                                    <strong>{{ $message }}</strong>
                                    </span>
                                    @enderror
                                </div>
                            </div>
                            <div id="program-div" class="row m-2 position-relative" hidden>
                                <div class="col-12">
                                    <select id="program" class="custom-select department_select" name="program">
                                        <option disabled selected hidden>Open list of programs</option>
                                        @foreach ($programs as $program)
                                            <option value="{{$program->program}}">{{$program->program}}</option>
                                        @endforeach
                                    </select>
                                     @error('program')
                                    <span class="invalid-feedback" role="alert">
                                    <strong>{{ $message }}</strong>
                                    </span>
                                    @enderror
                                </div>
                            </div>
                            <div class="row m-2 position-relative">
                                <div class="col-12">
                                    <button id="" type="submit" class="btn btn-primary col"><i class="bi bi-plus"></i> User</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>


    <script type="application/javascript">
    var faculties = <?php echo json_encode($faculties);?>;
    var vFaculties = faculties.filter(item => {
        return item.campus_id === 1;
    });
    var oFaculties = faculties.filter(item => {
        return item.campus_id === 2;
    });
    var departments = <?php echo json_encode($departments);?>;

    $(document).ready(function () {

        $('#role').change(function() {
            if($('#role').find(':selected').val() == 'department-head') {
                roleDpHeadOption();
            } else if($('#role').find(':selected').val() == 'program-director') {
                roleProgramDirOption();
            }
        });

        $('#campus').change( function() {
            // filter faculty based on campus
            if ($('#campus').find(':selected').text() == 'Vancouver') {
                // Hide text / show select
                campusDefaultOption();

                //Displays Vancouver Faculties
                // delete drop down items
                $('#faculty').empty();
                // populate drop down
                $('#faculty').append($('<option disabled selected hidden>Open list of faculties/schools</option>'));
                vFaculties.forEach (faculty => $('#faculty').append($('<option name="'+faculty.faculty_id+'" />').val(faculty.faculty).text(faculty.faculty)));
                // $('#faculty').append($('<option name="-1" />').val('Other').text('Other'));

                // enable the faculty select field
                if ($('#faculty').is(':disabled')) {
                    $('#faculty').prop('disabled', false);
                }
                // disable the department field
                if (!($('#department').is(':disabled'))) {
                    $('#department').empty();
                    $('#department').append($('<option disabled selected hidden>Open list of departments</option>'));
                    $('#department').prop('disabled', true);
                }

            } else if ($('#campus').find(':selected').text() == 'Okanagan') {
                // Hide text / show select
                campusDefaultOption();

                // Display Okangan Faculties
                // delete drop down items
                $('#faculty').empty();
                // populate drop down
                $('#faculty').append($('<option disabled selected hidden>Open list of faculties/schools</option>'));
                oFaculties.forEach (faculty => $('#faculty').append($('<option name="'+faculty.faculty_id+'" />').val(faculty.faculty).text(faculty.faculty)));
                // $('#faculty').append($('<option name="-1" />').val('Other').text('Other'));

                // enable the faculty select field
                if ($('#faculty').is(':disabled')) {
                    $('#faculty').prop('disabled', false);
                }
                // disable the department field
                if (!($('#department').is(':disabled'))) {
                    $('#department').empty();
                    $('#department').append($('<option disabled selected hidden>Open list of departments</option>'));
                    $('#department').prop('disabled', true);
                }

            } else {
                campusOtherOption();
            }

        });

        $('#faculty').change( function() {
            var facultyId = parseInt($('#faculty').find(':selected').attr('name'));

            // get departments by faculty if they belong to a faculty, else display all departments
            if (facultyId >= 0) {
                // Hide text / show select
                facultyDefaultOption();

                // delete drop down items
                $('#department').empty();
                // populate drop down
                $('#department').append($('<option disabled selected hidden>Open list of departments</option>'));
                var filteredDepartments = departments.filter(item => {
                    return item.faculty_id === facultyId;
                });
                filteredDepartments.forEach(department => $('#department').append($('<option />').val(department.department).text(department.department)));


                // $('#department').append($('<option />').val('Other').text('Other'));

                // enable the faculty select field
                if ($('#department').is(':disabled')) {
                    $('#department').prop('disabled', false);
                }

            } else {
                // Hide text / show select
                facultyOtherOption();
            }

        });

        $('#department').change( function() {
            if ($('#department').find(':selected').val() !== 'Other') {
                departmentDefaultOption();
            } else {
                departmentOtherOption();
            }
        });
    });

    function roleDpHeadOption() {
        // Hide text / show select
        $('#campus-div').prop( "hidden", false );
        $('#faculty-div').prop( "hidden", false );
        $('#department-div').prop( "hidden", false );
        $('#program-div').prop( "hidden", true );
        $('#campus').prop( "hidden", false );
        $('#campus').prop( "required", true );
        $('#campus-text').prop( "hidden", true );
        $('#campus-text').prop( "disabled", true );
        $('#faculty').prop( "hidden", false );
        $('#faculty').prop( "required", true );
        $('#faculty').prop( "disabled", true );
        $('#faculty-text').prop( "hidden", true );
        $('#faculty-text').prop( "disabled", true );
        $('#department').prop( "hidden", false );
        $('#department').prop( "required", true );
        $('#department').prop( "disabled", true );
        $('#department-text').prop( "hidden", true );
        $('#department-text').prop( "disabled", true );
        $('#program').prop( "hidden", true );

    }

    function roleProgramDirOption() {
        // Hide text / show select
        $('#campus-div').prop( "hidden", true );
        $('#faculty-div').prop( "hidden", true );
        $('#department-div').prop( "hidden", true );
        $('#program-div').prop( "hidden", false );
        $('#campus').prop( "hidden", true );
        $('#campus-text').prop( "hidden", true );
        $('#campus-text').prop( "disabled", true );
        $('#faculty').prop( "hidden", true );
        $('#faculty').prop( "disabled", true );
        $('#faculty-text').prop( "hidden", true );
        $('#faculty-text').prop( "disabled", true );
        $('#department').prop( "hidden", true );
        $('#department').prop( "disabled", true );
        $('#department-text').prop( "hidden", true );
        $('#department-text').prop( "disabled", true );
        $('#program').prop( "hidden", false );
        $('#program').prop( "required", true );
    }

    function departmentDefaultOption() {
        // Hide text / show select
        $('#department-text').prop( "hidden", true );
        $('#department-text').prop( "disabled", true );
    }

    function departmentOtherOption() {
        // Hide text / show select
        $('#department-text').prop( "hidden", false );
        $('#department-text').prop( "disabled", false );
    }

    function facultyDefaultOption() {
        // Hide text / show select
        $('#faculty-text').prop( "hidden", true );
        $('#faculty-text').prop( "disabled", true );
        $('#department').prop( "hidden", false );
        $('#department').prop( "disabled", false );
        $('#department-text').prop( "hidden", true );
        $('#department-text').prop( "disabled", true );
    }

    function facultyOtherOption() {
        // Hide text / show select
        $('#faculty-text').prop( "hidden", false );
        $('#faculty-text').prop( "disabled", false );
        $('#department').prop( "disabled", true );
        $('#department').prop( "hidden", true );
        $('#department').text('');
        $('#department-text').prop( "hidden", false );
        $('#department-text').prop( "disabled", false );
    }


    function campusDefaultOption() {
        // Hide text / show select
        $('#campus-text').prop( "hidden", true );
        $('#campus-text').prop( "disabled", true );
        $('#faculty').prop( "hidden", false );
        $('#faculty').prop( "disabled", false );
        $('#faculty-text').prop( "hidden", true );
        $('#faculty-text').prop( "disabled", true );
        $('#department').prop( "hidden", false );
        $('#department').prop( "disabled", false );
        $('#department-text').prop( "hidden", true );
        $('#department-text').prop( "disabled", true );
    }

    function campusOtherOption() {
        // Hide text / show select
        $('#campus-text').prop( "hidden", false );
        $('#campus-text').prop( "disabled", false );
        $('#faculty').prop( "disabled", true );
        $('#faculty').prop( "hidden", true );
        $('#faculty').text('');
        $('#faculty-text').prop( "hidden", false );
        $('#faculty-text').prop( "disabled", false );
        $('#department').prop( "disabled", true );
        $('#department').prop( "hidden", true );
        $('#department').text('');
        $('#department-text').prop( "hidden", false );
        $('#department-text').prop( "disabled", false );
    }
</script>
@endsection
