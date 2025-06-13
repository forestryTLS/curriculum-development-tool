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
                        <form>
                            <div class="row m-2 position-relative">
                            <div class="col-6">
                                <input id="" type="email" name="email" class="form-control" placeholder="john.doe@ubc.ca" aria-label="email" required>
                                <div class="invalid-tooltip">
                                    Please provide a valid email ending with ubc.ca.
                                </div> 
                            </div>
                            <div class="col-3">
                                <select class="form-select" id="" name="role">
                                    <option value="admin" selected>Admin</option>
                                    <option value="user">User</option>
                                </select>                   
                            </div>
                            <div class="col-3">
                                <button id="" type="submit" class="btn btn-primary col"><i class="bi bi-plus"></i> User</button>
                            </div>
                        </div>
                        </form>
                        <div class="row justify-content-center">
                            <div class="col-8">
                                <hr>
                            </div>
                        </div>
                        <table id="" class="table table-light borderless" >
                            <thead>
                                <tr class="table-primary">
                                    <th>Users</th>
                                    <th>Role</th>
                                    <th colspan="2" class="text-center w-25">Department/Program</th>
                                </tr>
                            </thead>

                            <tbody>
                            </tbody>
                        </table>   
                    </div>
                </div>
            </div>
        </div>
    </div>
@endsection