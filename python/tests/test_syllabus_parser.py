import app.syllabus_parser as sp
import os
from pathlib import Path


def test_syllabi_word_template_with_tabular_assessments():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"TEST101_2025W1_Word_Tabular_Assessments.docx"
    file_name = "TEST101_2025W1_Word_Tabular_Assessments.docx"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W1'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'Acknowledgement' # Tables are not detected in .docx files, 
                                                         # no other title pattern is folled in the file
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject \narea], focusing on the key concepts, issues, and practices that shape \nthe field. Students will explore the historical background, current \ntrends, and future directions of [subject area], engaging with a \nvariety of perspectives and resources. The course blends lectures, \ndiscussions, and applied activities to help students understand how \nideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational \ntheories as well as contemporary approaches, gaining insight into \nthe ways [subject area] influences academic research, industry \npractice, and everyday life. The course also offers opportunities to \nwork with real-world examples and case studies, encouraging \nstudents to make connections between abstract concepts and \npractical applications. \nThis description outlines the scope and nature of the course, \nproviding students with a clear sense of the themes and topics that \nwill be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the \nsyllabus.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].',
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].',
                                        'Evaluate and critique information or arguments using evidence- based reasoning.',
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.',
                                        'Explore the connections between theoretical knowledge and real- world practice.',
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)] # Tests the clean_assessment_and_weights function to remove multiple "\n" in assessment names

def test_syllabi_word_template_with_assessments_with_brackets():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"TEST101_2025W1_Word_Assessments_with_brackets.docx"
    file_name = "TEST101_2025W1_Word_Assessments_with_brackets.docx"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W1'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'Acknowledgement' # Tables are not detected in .docx files, 
                                                         # no other title pattern is folled in the file
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject \narea], focusing on the key concepts, issues, and practices that shape \nthe field. Students will explore the historical background, current \ntrends, and future directions of [subject area], engaging with a \nvariety of perspectives and resources. The course blends lectures, \ndiscussions, and applied activities to help students understand how \nideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational \ntheories as well as contemporary approaches, gaining insight into \nthe ways [subject area] influences academic research, industry \npractice, and everyday life. The course also offers opportunities to \nwork with real-world examples and case studies, encouraging \nstudents to make connections between abstract concepts and \npractical applications. \nThis description outlines the scope and nature of the course, \nproviding students with a clear sense of the themes and topics that \nwill be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the \nsyllabus.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].',
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].',
                                        'Evaluate and critique information or arguments using evidence- based reasoning.',
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.',
                                        'Explore the connections between theoretical knowledge and real- world practice.',
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]


def test_syllabi_pdf_template_with_tabular_assessments():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"TEST101_2025W1_PDF_Tabular_Assessments.pdf"
    file_name = "TEST101_2025W1_PDF_Tabular_Assessments.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W1'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'TEST Course Syllabus' 
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].', 
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'Evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'Explore the connections between theoretical knowledge and real-world practice.', 
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]


def test_syllabi_pdf_template_CLOs_without_bullets():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"TEST101_2025W1_PDF_Without_Bullet_CLOs.pdf"
    file_name = "TEST101_2025W1_PDF_Without_Bullet_CLOs.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W1'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'TEST Course Syllabus' 
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].', 
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'Evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'Explore the connections between theoretical knowledge and real-world practice.', 
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]
    

def test_syllabi_pdf_template_without_course_title_table():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"TEST101_2025W1_Without_Course_Title_table.pdf"
    file_name = "TEST101_2025W1_Without_Course_Title_table.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W1'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'COURSE SYLLABUS' #Course code is removed from the title
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].', 
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'Evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'Explore the connections between theoretical knowledge and real-world practice.', 
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]
    
def test_syllabi_file_name_without_course_code_number_and_term():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"FileNameWithoutCode&Term.pdf"
    file_name = "FileNameWithoutCode&Term.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W2'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'COURSE SYLLABUS' #Course code is removed from the title
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].', 
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'Evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'Explore the connections between theoretical knowledge and real-world practice.', 
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]


def test_syllabi_file_name_without_course_code_number_term_and_multiple_codes_in_file():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"FilenameWithoutCode&MultipleCodeInFile.pdf"
    file_name = "FilenameWithoutCode&MultipleCodeInFile.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W2'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'TEST Course Syllabus'
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].', 
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'Evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'Explore the connections between theoretical knowledge and real-world practice.', 
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]
    
    
def test_syllabi_different_layout():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"DifferentLayoutSyllabus.pdf"
    file_name = "DifferentLayoutSyllabus.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W2'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'TEST 101 2025W2: Test Course Syllabus'
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['To explain the core concepts, theories, and terminology related to [subject area].', 
                                        'To apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'To evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'To communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'To explore the connections between theoretical knowledge and real-world practice.', 
                                        'To integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]
    
    
def test_syllabi_different_layout_assessments_percentage_seperated():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"DifferentLayoutSyllabusWithComponentsPrecentageSeperated.pdf"
    file_name = "DifferentLayoutSyllabusWithComponentsPrecentageSeperated.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W2'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'TEST 101 2025W2: Test Course Syllabus'
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['To explain the core concepts, theories, and terminology related to [subject area].', 
                                        'To apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'To evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'To communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'To explore the connections between theoretical knowledge and real-world practice.', 
                                        'To integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('test assignments', 27), 
                                              ('test participation', 3), 
                                              ('test midterm', 40), 
                                              ('test individual final exam', 30)]
    

def test_syllabi_description_with_additional_section():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"TEST101_Syllabus_Description_With_Additional_Section.pdf"
    file_name = "TEST101_Syllabus_Description_With_Additional_Section.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W2'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'TEST Course Syllabus'
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus. \nTarget Audience \nThis course is intended for undergraduates who are interested in gaining knowledge and skills in \n[subject area]. It is especially suitable for students enrolled in forestry programs, as well as \nthose from related fields seeking to broaden their understanding of the topic. No prior experience \nin [subject area] is required unless otherwise noted in the prerequisites.'
    assert course_instance['goals'] == ['Explain the core concepts, theories, and terminology related to [subject area].', 
                                        'Apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].', 
                                        'Evaluate and critique information or arguments using evidence-based reasoning.', 
                                        'Communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.', 
                                        'Explore the connections between theoretical knowledge and real-world practice.', 
                                        'Integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]


def test_syllabi_CLOs_with_prefixed():
    BASE_DIR = Path(__file__).parent
    file_path = BASE_DIR /"data"/"syllabi"/"TEST101_2025W1_CLOs_with_prefixes.pdf"
    file_name = "TEST101_2025W1_CLOs_with_prefixes.pdf"
    course_instance = sp.get_course_from_text_file(file_path, file_name)
    assert course_instance['code'] == 'TEST'
    assert course_instance['number'] == 101
    assert course_instance['term'] == 'W1'
    assert course_instance['year'] == 2025
    assert course_instance['title'] == 'TEST Course Syllabus'
    assert course_instance['level'] == 'Undergraduate'
    assert course_instance['description'] == 'This course provides a comprehensive introduction to [subject area], focusing on the key \nconcepts, issues, and practices that shape the field. Students will explore the historical \nbackground, current trends, and future directions of [subject area], engaging with a variety of \nperspectives and resources. The course blends lectures, discussions, and applied activities to help \nstudents understand how ideas in this domain are developed, debated, and implemented. \nThroughout the term, students will gain exposure to foundational theories as well as \ncontemporary approaches, gaining insight into the ways [subject area] influences academic \nresearch, industry practice, and everyday life. The course also offers opportunities to work with \nreal-world examples and case studies, encouraging students to make connections between \nabstract concepts and practical applications. \nThis description outlines the scope and nature of the course, providing students with a clear sense \nof the themes and topics that will be covered. Specific learning objectives, assessment criteria, \nand expected outcomes are detailed in separate sections of the syllabus.'
    assert course_instance['goals'] == ['Be able to explain the core concepts, theories, and terminology related to [subject area].',
                                        'Be able to apply appropriate methods, tools, or frameworks to analyze problems and develop solutions within [subject area].',
                                        'Be able to evaluate and critique information or arguments using evidence-based reasoning.',
                                        'Be able to  communicate ideas and findings effectively in written, oral, or visual formats appropriate to the field.',
                                        'Be able to explore the connections between theoretical knowledge and real-world practice.',
                                        'Be able to integrate knowledge gained in class with real-world or interdisciplinary contexts.']
    assert course_instance['assessments'] == [('Test Assignments', 27), 
                                              ('Test participation', 3), 
                                              ('Test Midterm', 40), 
                                              ('Test Individual final Exam', 30)]

