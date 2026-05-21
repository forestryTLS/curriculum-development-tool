@extends('layouts.app')

@section('content')
<div class="mt-4 mb-5">
    <div class="row">
        <div class="col">
            <h3>Course: {{ $course->year }} {{ $course->semester }} {{ $course->course_code }} {{ $course->course_num }} {{ $course->section }}</h3>
            <h5 class="text-muted">{{ $course->course_title }}</h5>
        </div>
        <div class="col-auto">
            <a href="{{ route('courseWizard.step1', $course->course_id) }}" class="btn btn-outline-secondary btn-sm">
                <i class="bi bi-arrow-left"></i> Back to Course Wizard
            </a>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mt-3">{{ session('success') }}</div>
    @endif
    @if (session('error'))
        <div class="alert alert-danger mt-3">{{ session('error') }}</div>
    @endif
    @if ($errors->any())
        <div class="alert alert-danger mt-3">
            <ul class="mb-0">
                @foreach ($errors->all() as $err)
                    <li>{{ $err }}</li>
                @endforeach
            </ul>
        </div>
    @endif
    @if (request('upload_error') === 'too_large')
        <div class="alert alert-danger mt-3">
            The uploaded file is too large. The current server limit is {{ request('limit', '?') }}B.
            Please try a smaller file.
        </div>
    @endif

    <div class="card mt-4">
        <div class="card-header"><h5 class="mb-0">Coverage Analysis (dev)</h5></div>
        <div class="card-body">
            <p class="text-muted mb-0">
                Upload supporting PDFs. The indexer extracts text per page; the raw extraction is shown
                below for inspection. Search is provided by the system-wide content search feature.
            </p>
        </div>
    </div>

    <div class="card mt-3">
        <div class="card-header"><h6 class="mb-0">Upload Material</h6></div>
        <div class="card-body">
            @if ($canEdit)
                <form action="{{ route('course.materials.store', $course->course_id) }}" method="POST" enctype="multipart/form-data">
                    @csrf
                    <div class="row g-2 align-items-end">
                        <div class="col-md-8">
                            <label for="materialFile" class="form-label">PDF (max 50MB)</label>
                            <input type="file" id="materialFile" name="file" accept="application/pdf" class="form-control" required
                                onchange="validateMaterialSize(this)">
                            <small id="materialSizeFeedback" class="form-text text-danger d-none"></small>
                        </div>
                        <div class="col-md-4">
                            <button type="submit" class="btn btn-primary w-100">Upload</button>
                        </div>
                    </div>
                </form>
            @else
                <p class="text-muted mb-0">You have view-only access; uploads are disabled.</p>
            @endif
        </div>
    </div>

    <div class="card mt-3">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Extracted Materials</h6>
            <small class="text-muted">{{ $materials->count() }} file(s)</small>
        </div>
        <div class="card-body">
            @if ($materials->isEmpty())
                <p class="text-muted mb-0">No materials uploaded yet.</p>
            @else
                @if ($materials->contains(fn ($m) => in_array($m->status, ['PENDING', 'INDEXING'])))
                    <div class="alert alert-info py-2">
                        Some materials are still indexing. Refresh in a moment.
                    </div>
                @endif

                <div class="accordion" id="materialsAccordion">
                    @foreach ($materials as $material)
                        @php
                            $heading = 'materialHeading' . $material->id;
                            $body = 'materialBody' . $material->id;
                        @endphp
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="{{ $heading }}">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                                    data-bs-target="#{{ $body }}" aria-expanded="false" aria-controls="{{ $body }}">
                                    <div class="d-flex w-100 justify-content-between align-items-center pe-3">
                                        <div>
                                            <strong>{{ $material->file_name }}</strong>
                                            <small class="text-muted ms-2">
                                                {{ $material->page_count ?? '?' }} pages,
                                                {{ number_format($material->file_size / 1024, 1) }} KB,
                                                uploaded {{ $material->created_at->format('Y-m-d H:i') }}
                                                @if ($material->uploader) by {{ $material->uploader->name }} @endif
                                            </small>
                                        </div>
                                        <div>
                                            @switch($material->status)
                                                @case('INDEXED')
                                                    <span class="badge bg-success">Indexed</span>
                                                    @break
                                                @case('INDEXING')
                                                    <span class="badge bg-info text-dark">Indexing</span>
                                                    @break
                                                @case('PENDING')
                                                    <span class="badge bg-secondary">Pending</span>
                                                    @break
                                                @case('FAILED')
                                                    <span class="badge bg-danger" title="{{ $material->error_message }}">Failed</span>
                                                    @break
                                            @endswitch
                                        </div>
                                    </div>
                                </button>
                            </h2>
                            <div id="{{ $body }}" class="accordion-collapse collapse"
                                aria-labelledby="{{ $heading }}" data-bs-parent="#materialsAccordion">
                                <div class="accordion-body">
                                    <div class="d-flex gap-2 mb-3">
                                        <a class="btn btn-sm btn-outline-primary"
                                            href="{{ route('course.materials.download', ['course' => $course->course_id, 'materialId' => $material->id]) }}">
                                            <i class="bi bi-download"></i> Download original
                                        </a>
                                        @if ($canEdit)
                                            <form action="{{ route('course.materials.destroy', ['course' => $course->course_id, 'materialId' => $material->id]) }}"
                                                method="POST" onsubmit="return confirm('Delete this material and its extracted content?');" class="d-inline">
                                                @csrf
                                                @method('DELETE')
                                                <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
                                            </form>
                                        @endif
                                    </div>

                                    @if ($material->status === 'FAILED')
                                        <div class="alert alert-danger">
                                            <strong>Indexing failed.</strong>
                                            <div><code>{{ $material->error_message }}</code></div>
                                        </div>
                                    @elseif ($material->chunks->isEmpty())
                                        <p class="text-muted mb-0">No extracted content yet.</p>
                                    @else
                                        <p class="text-muted small">
                                            {{ $material->chunks->count() }} chunk(s) extracted. Showing raw text per page.
                                        </p>
                                        @foreach ($material->chunks as $chunk)
                                            <details class="mb-2">
                                                <summary>
                                                    <strong>Page {{ $chunk->page_number }}</strong>
                                                    <small class="text-muted">({{ str_word_count($chunk->content) }} words)</small>
                                                </summary>
                                                <pre class="bg-light border p-2 mt-2 mb-0" style="white-space: pre-wrap; max-height: 400px; overflow-y: auto;">{{ $chunk->content }}</pre>
                                            </details>
                                        @endforeach
                                    @endif
                                </div>
                            </div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>
</div>

<script>
    function validateMaterialSize(input) {
        const maxBytes = 50 * 1024 * 1024;
        const feedback = document.getElementById('materialSizeFeedback');
        if (input.files && input.files[0] && input.files[0].size > maxBytes) {
            const sizeMb = (input.files[0].size / 1024 / 1024).toFixed(1);
            feedback.textContent = `That file is ${sizeMb} MB; the maximum is 50 MB. Please choose a smaller file.`;
            feedback.classList.remove('d-none');
            input.value = '';
        } else {
            feedback.textContent = '';
            feedback.classList.add('d-none');
        }
    }
</script>
@endsection
