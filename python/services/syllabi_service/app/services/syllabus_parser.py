import pymupdf
import re
from collections import defaultdict
import nltk
import string
from nltk.corpus import stopwords
from tabula import read_pdf
from datetime import datetime


nltk.download('stopwords')

learning_goals_starting_words = ('demonstrate', 'develop', 'conduct', 'describe', 'understand', "outline", "diagnose", "show",
                      "sketch", "read", "recognize", "explain", "define", "make", "geocode", "produce", "utilize",
                      "acquire","complete", "compare", "identify", "provide", "evaluate", "prepare", "appreciate", "know",
                      "proficient", "efficiently", "perform", "create", "generate", "data handling and analyzing",
                      "importexport", "managing", "plan", "enhance", "explore", "have a thorough understanding",
                      "apply", "analyze", "interpret", "discuss", "suggest", "communicate", "give",
                      "be able to put", "be able to plot", "organize", "acheive", "become familiar",
                      "gain a foundation", "critically engage", "gain understanding", "gain specific understanding", "to understand",
                      "to become", "select", "design", "calculate", "incorporate", "working in groups",
                      "assess the challenges", "propose", "contrast the evolution", "name and describe", "integrate",
                      "manage large", "derive", "solve", "illustrate", "assess", "critically evaluate", "display",
                      "participate in inter-governmental", "follow the developments", "use simpler procedures",
                      "give specific examples", "given particular", "for each of these", "relate these concepts",
                      "thoughtfully reflect on", "clearly and concisely communicate", "summarize", "choose")

only_bullet_pattern = re.compile(r"^([(]?\d+(\.\d+)*[.)]?|[•\-–*¢●]|\([a-zA-Z]\))\s*")


def get_course_from_text_file(filePath: str, originalFileName: str) -> dict:
    try:
        doc = pymupdf.open(filePath)
    except Exception as e:
        raise Exception(f"Error opening file {filePath}: {str(e)}")
    
    course = {
            "code": "",
            "number": 0,
            "title": "",
            "term": "",
            "year": 0,
            "level": "",
            "description": "",
            "goals": [],
            "assessments": [],
            "topics": [],
            "materials": [],
    }
    
    doc_without_header = remove_header_and_footer(doc)
    code_and_number = find_course_code_and_number(doc, originalFileName)
    course["code"] = get_course_code(code_and_number)
    course["number"] = get_course_number(code_and_number)
    course["title"] = get_course_title(doc, course["code"], str(course["number"]), doc_without_header)
    term_of_offering = find_term_of_offering(doc, originalFileName)
    if term_of_offering is not None:
        course["term"] = get_encoded_term_of_offering(term_of_offering[0])        
        # If year is not found or is not a valid integer, default to current year
        try:
            course["year"] = int(term_of_offering[1])
        except ValueError:
            course["year"] = datetime.now().year
        except TypeError:
            course["year"] = datetime.now().year
    else:
        course["term"] = get_encoded_term_of_offering(term_of_offering)
        course["year"] = datetime.now().year
    course["level"] = get_level_of_study(course["number"])
    course["description"] = get_course_description(doc_without_header)
    course["goals"] = get_learning_goals(doc_without_header)
    assessments_and_weights = get_assessment_methods_and_weight(doc)
    course["assessments"] = encode_assessment_and_weight(assessments_and_weights)
    if originalFileName.lower().endswith(".docx"):
        course["topics"] = []
    else:
        course["topics"] = get_course_topics(doc, doc_without_header)
    course["materials"] = get_course_materials(doc, doc_without_header)

    return course


def get_course_code_from_file_name(fileName: str) -> str:
    """Returns the code for the from the file name if exists, otherwise return empty string"""
    
    # partsOfPath = filePath.split("\\")
    partsOfPath = fileName.split("/")
    fileName = partsOfPath[len(partsOfPath) - 1]
    pattern = r'([A-Za-z]{3,4})(?:[-_ ]?[Vv])?(?:[-_ ]*)?(\d{3})(?!\d)'
    # print(fileName)
    allCodeFound = re.findall(pattern, fileName)
    print(allCodeFound)
    if len(allCodeFound) > 0:
        return f"{allCodeFound[0][0].upper()} {allCodeFound[0][1]}"
    else:
        return ""


# def find_tables(filePath):
#     tables = read_pdf(filePath, pages='all')
#     return tables


def find_course_code_and_number(doc: pymupdf.Document, originalFileName: str) -> str| None:
    """Find the course code and number, given the name of file for the course syllabus and doc of the syllabus"""
    allCodesInFile = {}
    
    courseCodeFromFileName = get_course_code_from_file_name(originalFileName)

    if len(courseCodeFromFileName) != 0:
        return courseCodeFromFileName

    courseCodePattern = r'\b[A-Z]{3,4}(?:[ ]*)?\d{3}(?=[A-Z]?(?:\b|\\))'
    
#     courseCodePattern = re.compile(
#     r'(?:\b([A-Z]{3,4}\s*\d{3})(?=[A-Z]?(?:\b|\\)))'                 
#     r'|(?:\b(?:\w+\s+){0,3}([A-Z]{3,4}\s*\d{3})(?:[:.\-\s])(?:\s*\w+){0,5})'  
# )
    
    fileText = ""
    for page in doc:
        listOfText = page.get_text("text")
        fileText = fileText + " \n" + listOfText

    allCodesFound = list(re.finditer(courseCodePattern, fileText))
    for match in allCodesFound:
        # code = match.group(1) or match.group(2)
        code = match.group()
        pos = match.start()
        if code in allCodesInFile:
            allCodesInFile[code]["numOccurrence"] = allCodesInFile[code]["numOccurrence"] + 1
            if pos < allCodesInFile[code]["pos"]:
                allCodesInFile[code]["pos"] = pos
        else:
            allCodesInFile[code] = {"numOccurrence": 1, "pos": pos}

    # print("All Codes in File ", allCodesInFile)

    if len(allCodesInFile) == 0:
        return 

    maxOccurance = max(v["numOccurrence"] for v in allCodesInFile.values())

    coursesWithMaxOccurance = []
    for key, value in allCodesInFile.items():
        if value["numOccurrence"] == maxOccurance:
            coursesWithMaxOccurance.append(key)
    # print(coursesWithMaxOccurance)

    if len(coursesWithMaxOccurance) == 1:
        return coursesWithMaxOccurance[0]
    else:
        # More than 1 course has no. of occrances = maxOccurance therefore, find course that appears first in the text in terms of position in the document
        courseCodeThatAppearsFirst = ""
        minPos = float("inf")
        for course in coursesWithMaxOccurance:
            if allCodesInFile[course]["pos"] < minPos:
                courseCodeThatAppearsFirst = course
                minPos = allCodesInFile[course]["pos"]
        return courseCodeThatAppearsFirst


def get_course_number(course: str| None) -> int:
    """Returns the course number, given string of course code and number
        If no course number found, returns 999"""
    # course = find_course_code_and_number(filePath)
    if not course or len(course) == 0:
        return 999
    match = re.search(r'(\d{3,})', course)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return 999
        except TypeError:
            return 999
    return 999


def get_course_code(course: str| None) -> str:
    """Returns the course code, given string of course code and number
        If no course code found, returns empty TEST"""
    # course = find_course_code_and_number(filePath)
    if not course or len(course) == 0:
        return "TEST"
    if " " in course:
        codeAndNumber = course.split(" ")
        if len(codeAndNumber) >= 1 and len(codeAndNumber[0]) > 0:
            return codeAndNumber[0]
        else:
            return "TEST"
    else:
        match = re.match(r'([a-zA-Z]+)(\d+)', course)
        if match:
            return match.group(1)
        else:
            return "TEST"


def find_table_get_title(page: pymupdf.Page) -> str | None:
    """Returns course title if found in a table, given the page of the syllabus"""
    title_col_heading = {"course title"}
    tables = page.find_tables()
    if tables:
        for table in tables.tables:
            # print(table.header.names)
            title_table = table.extract()   # title_table: List[List[str]]
            # print(title_table)
            
            # Filter out any sublists (rows) from title_table where all items are None or empty strings, i.e. the row is empty
            cleaned_table = [sublist for sublist in title_table if any(item not in (None, '') for item in sublist)]
            
            # From each sublist in cleaned_table, remove any items that are None or empty strings
            cleaned_nested_table = [[item for item in sublist if item not in (None, '')]
                                    for sublist in cleaned_table]
            
            # Find the first (index, value) in the first row of cleaned_nested_table (as the first row would contain headings of columns of the table) where the value is not None and its lowercase form appears in title_col_heading.
            # If no such value is found, return None.
            name_match = next(((i, val) for i, val in enumerate(cleaned_nested_table[0]) if
                               val is not None and val.lower() in title_col_heading), None)
            
            if name_match:
                index_name_column = name_match[0]
                # print(index_name_column)
                # print(title_table)
                try:
                    return cleaned_nested_table[1][index_name_column]
                except:
                    return None


def get_course_title(doc: pymupdf.Document, code: str, number: str, doc_without_header: list[str])-> str:
    """Returns the course title, given doc of the syllabus, course code and course number """

    courseCode = code + " " + number
    print("Course Code: ", courseCode)
    titlePatterns = [r'Course Title[:\s]*([^\n]+)',
                     r'Course title[:\s]*([^\n]+)',
                     r'course Title[:\s]*([^\n]+)',
                     r'Course Name[:\s]*([^\n]+)',
                     rf'\b{re.escape(courseCode)}:[^\n]*\s*\n',
                     rf'\b{re.escape(courseCode)}\s*–\s*[^\n]*\s*\n',
                     rf'[^\n]+\s*:\s*\b{re.escape(courseCode)}\s*\n',
                     rf'[^\n]+\s*:\s*[A-Z]{{4}}\s*\d{{3}}\s*\n']

    allTitlesInFile = {}
    firstLine = ""

    for page in doc:
        listOfText = page.get_text("text")
        possibleName = find_table_get_title(page)
        if possibleName:
            return possibleName
        for pattern in titlePatterns:
            allTitlesFound = re.findall(pattern, listOfText)
            for title in allTitlesFound:
                if title in allTitlesInFile:
                    allTitlesInFile[title] = allTitlesInFile[title] + 1
                else:
                    allTitlesInFile[title] = 1
    # print(allTitlesInFile)
    
    for page_text in doc_without_header:
        lines = page_text.split('\n')
        
        # Get the first non-empty line that is not just a number and strip any leading/trailing whitespace, or set to an empty string if no such line exists
        firstLine = next((line for line in lines if line.strip() and not line.strip().isnumeric()), "").strip()
        
        if len(firstLine) < 1:
            #Fallback to course code and number if no title found
            firstLine = courseCode
        break

    if len(allTitlesInFile.values()) == 0:
        return firstLine

    maxOccurance = max(allTitlesInFile.values())

    coursesWithMaxOccurance = [] # list of titles with maximum occurances, excluding those with 'code', 'section' or 'number' in them
    for key, value in allTitlesInFile.items():
        count = 0
        for word in ("code", "section", "number"):
            if re.search(rf'\b{re.escape(word)}\b', key, re.IGNORECASE):
                count += 1
                if count > 1:
                    break
        if count > 1:
            continue
        if value == maxOccurance:
            coursesWithMaxOccurance.append(key)
    # print(coursesWithMaxOccurance)

    if len(coursesWithMaxOccurance) >= 1:
        title = coursesWithMaxOccurance[0]
        # filter out titles that are just course code and number
        replacements = [code, number, '\n']
        for item in replacements:
            title = title.replace(item, "")
        title = title.translate(str.maketrans('', '', string.punctuation))
        if title.lower().strip() in ("course code number", "course code"):
            return courseCode
        title = title.strip()
        # Remove leading dash if present in cases where titles are of the form "CODE NUMBER - TITLE"
        if title.startswith("–"):
            title = title[1:]
        if title == "":
            return firstLine
        return title
    return firstLine


def get_term_and_year_from_regex(year: str|None, match: re.Match) -> tuple[str, str|None] | str:
    """Returns the term and year, given the regex match and year if found in the match"""
    term_patterns = [
        (r'(fall|w1|winter[\s_]?term[\s_]?1|term[\s_]?1)', "Winter Term 1"),
        (r'(w2|winter[\s_]?term[\s_]?2|term[\s_]?2)', "Winter Term 2"),
        (r'(s1|summer[\s_]?term[\s_]?1)', "Summer Term 1"),
        (r'(s2|summer[\s_]?term[\s_]?2)', "Summer Term 2"),
    ]
    for pattern, term in term_patterns:
        if re.search(pattern, match.group(1), re.IGNORECASE):
            if year:
                return (term, year)
            else:
                return term
    return (match.group(1), year)



def find_term_of_offering(doc: pymupdf.Document, filePath: str)-> tuple[str, str| None] | None:
    """Finds the term of offering and year, given the doc of the syllabus and file path"""
    
    term_regex = re.compile(
        r'(Fall[ _]?20\d{2}|Winter[ _]?Term[ _]?[12](?!\d)|20\d{2}[ _]?[WS][ _]?[12](?!\d)|Term[ ]?[12][ ]?20\d{2})',
        re.IGNORECASE
    )
    term_found = None

    month_variants = {
        'January': ['January', 'Jan'],
        'February': ['February', 'Feb'],
        'March': ['March', 'Mar'],
        'April': ['April', 'Apr'],
        'May': ['May'],
        'June': ['June', 'Jun'],
        'July': ['July', 'Jul'],
        'August': ['August', 'Aug'],
        'September': ['September', 'Sep', 'Sept'],
        'October': ['October', 'Oct'],
        'November': ['November', 'Nov'],
        'December': ['December', 'Dec']
    }

    # Compile regex patterns for each month variant and store them in a dictionary with full month names as keys
    month_regexes = {
        month: re.compile(r'\b(?:' + '|'.join(variants) + r')\b')
        for month, variants in month_variants.items()
    }

    month_counts = {}

    # Check pattern in filename
    partsOfPath = filePath.split("/")
    fileName = partsOfPath[len(partsOfPath) - 1]
    match = term_regex.search(fileName)
    if match:
        year = re.search(r'(20\d{2})', match.group(1), re.IGNORECASE)
        if year:
            year = year.group(1)
            return get_term_and_year_from_regex(year, match)
        else:
            term_found = get_term_and_year_from_regex(None, match)

    year_counts = {}

    # Check in the file
    for page in doc:
        listOfText = page.get_text("text")
        
        # Check for term and year pattern in the text of the page
        match = term_regex.search(listOfText)
        if match:
            year = re.search(r'(20\d{2})', match.group(1), re.IGNORECASE)
            if year:
                year = year.group(1)
                return get_term_and_year_from_regex(year, match)
            else:
                term_found = get_term_and_year_from_regex(None, match)

        # Count occurrences of each month in the text of the page for determining term
        for month, regex in month_regexes.items():
            if month in month_counts:
                month_counts[month] += len(regex.findall(listOfText))
            else:
                month_counts[month] = len(regex.findall(listOfText))

        # Count occurrences of each year in the text of the page for determining year
        years = re.findall(r'(20\d{2})', listOfText)
        for year in years:
            if year in year_counts:
                year_counts[year] += 1
            else:
                year_counts[year] = 1

    maxOccurance = max(month_counts.values())

    monthWithMaxOccurance = None
    for key, value in month_counts.items():
        if value == maxOccurance and monthWithMaxOccurance is None:
            monthWithMaxOccurance = key
            break

    # Check for year in filename, if not found, use the year with maximum occurances in the text        
    yearMatch = re.search(r'(20\d{2})', fileName)
    if yearMatch:
        final_year = yearMatch.group(1)
    else:
        final_year = None
        if len(year_counts) > 0:
            yearMaxOccurance = max(year_counts.values())
        else:
            yearMaxOccurance = None
        if yearMaxOccurance is not None:
            for key, value in year_counts.items():
                if value == yearMaxOccurance and final_year is None:
                    final_year = key
                    break
                    
    if term_found and final_year:
        return (term_found, final_year)

    if monthWithMaxOccurance in ("January", 'February', 'March', 'April'):
        # Assuming that the schedule is mentioned in the syllabus because of which the year has maximum occurances
        if len(year_counts) > 0:
            yearMaxOccurance = max(year_counts.values())
        else:
            yearMaxOccurance = None
            
        # If the year with maximum occurances is the final_year and the next year is not present in the text, then decrement the final_year by 1 since a course offered in Jan-April 2024 is likely to be
        # part of Winter Term 2 of the academic year 2023
        if final_year in year_counts.keys() and year_counts[final_year] == yearMaxOccurance and maxOccurance > 0 and \
                (str(int(final_year) + 1) not in year_counts.keys()):
            final_year = str(int(final_year) - 1)
        return ("Winter Term 2", final_year)
    elif monthWithMaxOccurance in ('September', 'October', 'November', 'December'):
        return ("Winter Term 1", final_year)
    elif monthWithMaxOccurance in ("May", "June"):
        return ("Summer Term 1", final_year)
    elif monthWithMaxOccurance in ("July", "August"):
        return ("Summer Term 2", final_year)
    else:
        return None


def get_encoded_term_of_offering(term: str| None) -> str:
    """Returns the encoded term of offering for mapping tool, given the term of offering, otherwise returns the term based on current month"""
    
    termWithCode = {"Winter Term 2": "W2", "Winter Term 1": "W1", "Summer Term 1": "S1", "Summer Term 2": "S2"}
    
    if term in termWithCode:
        return termWithCode[term]
    else:
        currentMonth = datetime.now().month
        if currentMonth < 5: #Jan -Apr
            return "W2"
        elif currentMonth > 8: #Sept - Dec
            return "W1"
        elif currentMonth > 4 and currentMonth < 7: #May - Jun
            return "S1"
        else:
            return "S2" #July - Aug
        
    

def normalize_header_footer(text: str) -> str:
    """Normalize only if text looks like a page number/footer."""
    patterns = [
        r'Page\s+\d+',              # "Page 12"
        r'\d+\s*/\s*\d+',           # "12/50"
        r'\d+\s+of\s+\d+',          # "12 of 50"
        r'Page\s+\d+\s+of\s+\d+',   # "Page 12 of 50"
        r'^\d+$',                   # just digits
        r'^\d+\s+.+$',              # "1 Some text"
        r'^-\s*\d+\s*-$',           # "- 1 -"
    ]
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return re.sub(r'\d+', '<NUM>', text)
    return text

def remove_header_and_footer(doc: pymupdf.Document)-> list[str]:
    """Identifies and removes header and footer from the text document. The top 10% and bottom 10% of each page are considered for header and footer detection."""
    
    top_texts = defaultdict(int)
    bottom_texts = defaultdict(int)

    pages = []

    for page in doc:
        page_blocks = []
        page_height = page.rect.height
        top_y_threshold = 0.1 * page_height
        bottom_y_threshold = 0.9 * page_height
        blocks = page.get_text("blocks")
        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            strippedText = text.strip()
            normalizedText = normalize_header_footer(strippedText)
            page_blocks.append((strippedText, normalizedText))
            if y0 < top_y_threshold:
                top_texts[normalizedText] += 1
            elif y0 > bottom_y_threshold:
                bottom_texts[normalizedText] += 1
        pages.append(page_blocks)

    min_occurrence = int(0.8 * len(doc))
    header_candidates = {t for t, count in top_texts.items() if count >= min_occurrence}
    footer_candidates = {t for t, count in bottom_texts.items() if count >= min_occurrence}

    # Comment this out if you don't want to see the header and footer candidates printed
    print("Header candidates:", header_candidates)
    print("Footer candidates:", footer_candidates)

    cleaned_pages = []

    for page in pages:
        page_text = []
        for block in page:
            if block[1] not in header_candidates and block[1] not in footer_candidates:
                page_text.append(block[0])
        cleaned_pages.append("\n".join(page_text))

    return cleaned_pages


def get_bullet_type(line: str) -> str | None:
    """Identifies and returns the type of bullet in a line"""
    match = re.match(only_bullet_pattern, line)
    if match:
        return match.group(0)  # Return the matched prefix (e.g., "1. ", "- ", etc.)
    return None


def is_bullet_patterns_matching(pattern1: str| None, pattern2: str| None)-> bool:
    """Returns True if the two given bullet patterns are of the same type, otherwise False"""
    match1 = re.match(only_bullet_pattern, pattern1)
    match2 = re.match(only_bullet_pattern, pattern2)

    if not match2 or not match1:
        return False

    bullet1 = match1.group(1)
    bullet2 = match2.group(1)
    
    digit_bullet_pattern = re.compile(r"[(]?\d+(\.\d+)*[.)]?")
    possible_bullets = "•-–*¢●"

    if re.match(digit_bullet_pattern, bullet1) and re.match(digit_bullet_pattern, bullet2):
        return bullet1.count('.') == bullet2.count('.')
    elif bullet1 in possible_bullets and bullet2 in possible_bullets:
        return bullet1 == bullet2
    elif "(" in bullet1 and "(" in bullet2: # checking if both are of the form (a) or (1)
        mid1 = ""
        mid2 = ""
        if len(bullet1) >= 2:
            mid1 = bullet1[1]
        if len(bullet2) >= 2:
            mid2 = bullet2[1]
        return bullet1.count("(") == bullet2.count("(") and bullet1.count(")") == bullet2.count(")") \
               and ((mid1.isalpha() and mid2.isalpha()) or (mid1.isdigit() and mid2.isdigit()))
    else:
        return False


def is_only_bullet(currItem):
    """Returns true if given string only contains bullet and whitespace"""
    return bool(re.fullmatch(only_bullet_pattern, currItem))


def is_learning_goals_complete(line: str, goals: list[str], currentItem: str, bullet_pattern: re.Pattern[str], currIndex: int, lines: list[str], objective_pattern: str):
    """Returns true if learning goals section is complete, otherwise False
    
    parameters:
        line: current line being processed
        goals: list of learning goals found so far
        currentItem: current learning goal being processed
        bullet_pattern: regex pattern to identify bullets
        currIndex: index of current line in the list of lines
        lines: list of all lines in the document
        objective_pattern: pattern of bullet used in learning goals section
    
    The learning goals section is considered complete if:
    - the current line is in uppercase or title case or is empty, and
    - there are at least 2 learning goals found so far, or the current learning goal being processed has more than 5 characters, and
    - the current line does not contain a bullet, and
    - the current line does not start with any of the common starting words for learning goals, and
    - the next line (if exists) does not start with any of the common starting words for learning goals, and    
    - the next line (if exists) does not contain bullet and the next line's bullet pattern does not match the objective_pattern i.e. the bullet pattern of the learning goals 
    
    """
    return (line.isupper() or line.istitle() or line == "") and (len(goals) > 1 or (currentItem and len(currentItem) > 5)) \
           and not bullet_pattern.match(line) and not line.strip().lower().startswith(learning_goals_starting_words) \
           and not ((currIndex + 1 < len(lines)) and (lines[currIndex + 1].lower().startswith(learning_goals_starting_words) or
                                                      (objective_pattern and bullet_pattern.match(lines[currIndex + 1]) and
                                                       is_bullet_patterns_matching(objective_pattern, get_bullet_type(lines[currIndex + 1])))))


def get_learning_goals(doc: list[str]) -> list[str]:
    """Returns a list of learning goals, given the doc of syllabus without header and footer"""
    
    goals = []
    currentItem = ""
    headingFound = False
    patternFound = False
    firstGoal = True
    objective_pattern = ""

    expected_headings = {"course learning objectives", "learning outcomes", "learning objectives", "objectives:",
                         "learning goals", "course objectives", "course goals and outcomes", "learning objectives:",
                         "learning outcomes:", "academic objectives", "course-level learning outcomes",
                         "student learning outcomes:", "course objectives:", "learning outcome:",
                         "learning outcomes/ objectives", "after completing this course you will be able to:",
                         "learning objectives and outcomes:", "learning outcomes: wood mechanics",
                         "course learning outcomes:", "academic objectives:"}
    
    # Prefixes with which learning goals may start, helpful when there are no bullets
    prefixes = ("", "be able to", "will be able to", "be", "students will be able to")    
    
    # Characters that if a learning goal ends with, then it marks the end of that learning goal. Helpful when there are no bullets
    ending_chars = (";")

    bullet_pattern = re.compile(r"""^((?!\d+/\d+)([(]?\d+(\.\d+)*[.)]?)|[•\-–*¢●]|\([a-zA-Z]\))\s*.*""", re.VERBOSE)

    for page in doc:
        lines = page.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not headingFound and bullet_pattern.match(line):
                line = only_bullet_pattern.sub("", line)

            if line.lower() in expected_headings:
                headingFound = True
                if len(goals) != 0:
                    goals = []
                    currentItem = ""
                    firstGoal = True
                    objective_pattern = ""
                    patternFound = False
                i = i + 1
                continue

            if headingFound:
                if is_learning_goals_complete(line,goals, currentItem, bullet_pattern, i, lines, objective_pattern):
                    if currentItem:
                        goals.append(currentItem.strip())
                        headingFound = False
                        currentItem = ""
                    headingFound = False
                    break

                clean_line = re.sub(r'[^\w\s]', '', line.strip().lower())
                if bullet_pattern.match(line):
                    if firstGoal:
                        objective_pattern = get_bullet_type(line)
                        firstGoal = False
                    if currentItem:
                        goals.append(currentItem.strip())
                        currentItem = ""
                    if is_bullet_patterns_matching(objective_pattern, get_bullet_type(line)):
                        currentItem = line
                        patternFound = True
                    elif len(goals) < 2 and (len(goals) > 0 and is_only_bullet(goals[0]) and not is_bullet_patterns_matching(objective_pattern, get_bullet_type(line))):
                        objective_pattern = get_bullet_type(line)
                    else:
                        break
                elif patternFound and line:
                    currentItem = currentItem + " " + line
                elif any(clean_line.split()[:len((f"{prefix} {word}").strip().split())] == (f"{prefix} {word}").strip().lower().split() for prefix in prefixes
                         for word in learning_goals_starting_words): # If cleaned line starts with any of the combinations of prefixes and learning_goals_starting_words, then it is a learning goal
                    if currentItem:
                        goals.append(currentItem)
                    currentItem = line
                elif currentItem and line.strip().endswith(ending_chars):
                    currentItem = currentItem + " " + line
                    goals.append(currentItem)
                    currentItem = ""
                elif currentItem:
                    currentItem = currentItem + " " + line

            i = i + 1

    if currentItem:
        goals.append(currentItem.strip())
        currentItem = ""

    finalGoals = [only_bullet_pattern.sub("", goal) for goal in goals] # Remove any leading bullets from the learning goals

    # Comment this out if you don't want to see the learning goals printed
    # for goal in finalGoals:
    #     print("* ", goal)

    return finalGoals


def get_level_of_study(courseNumber: int) -> str:
    """Returns course level of study undergraduate or graduate, given course number. Course withe course numbers in range [100, 499] are undergraduate courses, otherwise graduate.
        By default the level is undergraduate"""
    
    # courseNumber = get_course_number(filePath)
    
    try:
        numInt = int(courseNumber)
        if numInt < 500:
            return "Undergraduate"
        return "Graduate"
    except ValueError:
        return "Undergraduate"
    except TypeError:
        return "Undergraduate"


def remove_stopwords(line: str) -> str:
    """Removes stopwords from the given line and returns the line without stopwords"""
    
    stop_words = set(stopwords.words('english'))
    words = re.findall(r'\b\w+\b', line)
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)


def is_heading(line: str, onlyUpper: bool, containsBullet: bool, bulletPattern: str) -> bool:
    """Returns true if a line is a heading, otherwise False"""

    # These following headings are generally a part of course description and should not be considered as headings for the purpose of stopping extraction of course description
    part_of_description_headings = {"rationale", "objectives", "target audience", "objective",
                                    "prerequisite:", "description:"}

    removed_punctuation = line.replace(":", "")

    if line.lower() in part_of_description_headings or removed_punctuation.lower() in \
            part_of_description_headings:
        return False
    if re.match(r'[A-Z]{4}[ ]?\d{3}', line): # To avoid lines that are just course codes
        return False

    # General headings that follow the course description section, and at which point the extraction of course description should stop
    headings = {"academic objectives", "learning outcomes"} # Can add more if needed
    
    #only_bullet_pattern = re.compile(r"^(\d+(\.\d+)*[.)]?|[•\-–*¢●]|\([a-zA-Z]\))\s*")

    # Check if given line starts with a bullet if containsBullet is True, and if the bullet pattern of given line matches bulletPattern, then this is a heading for next section 
    if containsBullet and re.search(only_bullet_pattern, line):
        bullet = get_bullet_type(line)
        if is_bullet_patterns_matching(bullet, bulletPattern):
            return True

    if len(line.split()) <= 3:
        line = remove_stopwords(line)
        if onlyUpper:
            if line.isupper():
                return True
            return False
        if line.isupper() or line.istitle():
            return True
        if line.lower() in headings:
            return True
    return False


def get_course_description(doc: list[str]) -> str:
    """Returns the text for the course description section, given the doc of syllabus without header and footer"""
    
    # doc = remove_header_and_footer(filePath)
    description = ""
    headingFound = False
    patternFound = False
    terminateFunction = False
    onlyUpperHeading = False
    containsBullet = False
    bulletType = ""
    headingLine = ""

    bullet_pattern = re.compile(r"^(\d+(\.\d+)*[.)]?|[•\-–*¢●]|\([a-zA-Z]\))\s*.*")
    # only_bullet_pattern = re.compile(r"^(\d+(\.\d+)*[.)]?|[•\-–*¢●]|\([a-zA-Z]\))\s*")

    expected_headings = {"course description", "course overview", "course structure", "why does this course matter?",
                         "course summary:", "course overview, content and objectives",
                         "course description – the big questions", "course description:", "course background",
                         "short description:", "course format:", "overview:", "course objective:", "course summary",
                         "course information:", "description"}
    
    for page in doc:
        if terminateFunction:
            break
        # listOfText = page.get_text("text")
        lines = page.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Checks if line starts with a bullet if heading not found yet, and removes the bullet for further processing and sets containsBullet to True to help in heading detection
            if not headingFound and bullet_pattern.match(line):
                if re.search(only_bullet_pattern, line):
                    bulletType = get_bullet_type(line)
                    line = only_bullet_pattern.sub("", line)
                    containsBullet = True

            removed_punctuation = line.replace(":", "")

            if not headingFound and (line.lower() in expected_headings or removed_punctuation.lower() in expected_headings):
                headingFound = True
                
                # Check if the heading is in all uppercase to help in heading detection
                if line.isupper():
                    onlyUpperHeading = True
                i = i + 1
                headingLine = line.lower()
                continue
            elif not headingFound:
                bulletType = ""
                containsBullet = False

            if headingFound:
                if is_heading(line, onlyUpperHeading, containsBullet, bulletType):
                    headingFound = False
                    if len(description) > 15:  # Threshold for minimum length of description section
                        terminateFunction = True
                        break

                else:
                    description = description + " \n" + line
            i = i + 1

    description = description.strip()
    cleaned_desc = description.replace('\xa0', '')

    return cleaned_desc


def clean_and_validate_assessment_weight_match(matches: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Returns True if number of components in and percentages in the given list of matches is same, removes components
    which are all in caps assuming that are headings"""
    
    comps = []
    percs = []
    if len(matches) == 1:
        for comp_text, perc_text in matches:  # unpack each tuple inside the loop
            
            comps.extend([c for c in comp_text.split('\n') if not c.isupper()])
            percs.extend(perc_text.split('\n'))
    else:
        for comp_text, perc_text in matches:  # unpack each tuple inside the loop
            comps.extend([comp_text.split('\n')[-1]]) # only take the last line of component text assuming that is the actual component
            percs.extend(perc_text.split('\n'))

    # Check if number of components equals number of percentages
    if len(comps) == len(percs):
        return True
    else:
        return False


def get_assessment_and_weight_separated_in_different_lines(lowerListOfText: str) -> list[tuple[str, str]]:
    '''Returns list of tuples of assessment methods and their corresponding weightage, given the text of the syllabus where components and percentages are in different lines
    This is to identify cases where components and percentages are in different lines but in the same section of the syllabus like below:
    Components
    Assignment 1
    Assignment 2
    Midterm
    Percentage
    10%
    10%
    30%
    '''
    lines = [line.strip() for line in lowerListOfText.split('\n') if line.strip() != '']
    # Find indexes of the headings "component" and "percentage"
    try:
        comp_idx = next(i for i, line in enumerate(lines) if line.lower() in ("component", "components")) # find index of first occurrence of "component" or "components"
        perc_idx = next(i for i, line in enumerate(lines) if line.lower() in ("percentage", "points/marks")) # find index of first occurrence of "percentage" or "points/marks"
    except StopIteration:
        return []

    # Extract components (all lines after component until percentage)
    components = lines[comp_idx + 1:perc_idx]
    # Extract percentages after "Percentage" heading until non-percentage pattern appears
    pattern = re.compile(r'^\d+%(\s+each\s+\(\d+%\s+total\))?$')

    percentages = []
    for line in lines[perc_idx + 1:]:
        if (pattern.match(line) or 'each' in line.lower() and 'total' in line.lower()):  # only matches lines like "10%"
            percentages.append(line)
        else:
            break  # stop when pattern doesn't match

    # Pair components with percentages (zip, truncate to shorter length)
    assessment_and_weight = list(zip(components, percentages))
    return assessment_and_weight


def clean_assessment_and_weights(allMatches: list[tuple[str, str]])->list[tuple[str, str]]:
    """ Returns cleaned list of assessment and weight, involves removing unessential portions identified by cerain keywords,
    presence of letter grades, new lines"""
    
    exclude_keywords = {"late", "penalty", "deduct", "approximately", "student", "please",
                        "may", "passing", "it", "must", "percentage", "deadline", "their", "there", "will",
                        "least", "reduced", "excellent", "fair", "good", "worth", "additional", "reduction",
                        "your", "than", "pass"}
    grades = {"A", "A-", "B", "B-", "C", "C-", "D", "F (Fail)", "F"}

    # Filter to only include elements of allMatches where no keyword from exclude_keywords appears in the assessment name. 
    # If \n is present in the assessment name then check for keywords only in the last line after \n
    filtered = [item for item in allMatches if
                not any(keyword in (item[0].split('\n')[-1].lower().split() if '\n' in item[0] else item[0].lower().split())
                    for keyword in exclude_keywords)]
    
    # Also remove any entries that are equal to 100 in weight
    filtered = [item for item in filtered if item[1] != 100 and item[1] != "100"]
    
    remove_new_lines = []
    for label, percent in filtered:
        if label in grades: # Some syllabi contain tables with letter grades and their corresponding percentage weight, which should be excluded
            continue
        if len(label.strip()) < 3: # Exclude labels that are too short to be meaningful
            continue
        if '\n' in label: 
            if label.count('\n') == 1:
                # If only one new line is present, then check if the portion before new line is in uppercase, if yes then remove it
                before, after = label.split('\n', 1)
                if before.strip().isupper():
                    label = after.strip()
            else: 
                # If multiple new lines are present, then keep only the portion after the last new line
                split_lines = label.split("\n") 
                label = split_lines[len(split_lines) - 1].strip()
        remove_new_lines.append((label.strip(), percent))
    return remove_new_lines

def get_assessment_weight_from_table(tables: pymupdf.table.TableFinder) -> list[tuple[str, str]] | None:
    """Returns assessment methods along with their corresponding weightage, given the tables of the course syllabus"""
    
    assessment_name_col_heading = {"item", "assessment", "graded activities", "component", "activity", "assignment",
                            "category", "components", "module", "type", "grading component", "evaluations",
                            "learning assessment", "grade component", "graded activities/assignments",
                            "winter term I", "winter term II", "exams and problem sets"}
    assessment_mark_col_heading = {"mark", "percentage", "marks", "weight (%)", "weight", "% of final grade",
                            "total weight", "percentage of final grade", "assignment weight", "%", "weighting",
                            "pts (/100)", "percent of final grade", "% final mark", "percent of grade", "grade weight"}
    
    for table in tables.tables:
        assessment_table = table.extract() #assessment_table is of type list 
        
        #Clean the table by removing empty rows i.e. rows where all elements are None or empty strings
        cleaned_table = [sublist for sublist in assessment_table if any(item not in (None, '') for item in sublist)]
        
        # Further clean each row by removing None or empty string elements
        cleaned_nested_table = [[item for item in sublist if item not in (None, '')]
                                for sublist in cleaned_table]
        
        # Identify the index of the assessment column
        name_match = next(((i, val) for i, val in enumerate(cleaned_nested_table[0]) if
                                   val is not None and val.lower() in assessment_name_col_heading), None)
        
        # Identify the index of the mark/weight column
        mark_match = next(((i, val) for i, val in enumerate(cleaned_nested_table[0]) if
                                   val is not None and val.lower() in assessment_mark_col_heading), None)
        
        if name_match and mark_match:
            index_name_column = name_match[0]
            index_mark_column = mark_match[0]
            assessment_table = cleaned_nested_table
            assessment_and_weight = []
            for i in range(1, len(assessment_table)):
                #print("From Inside Loop", assessment_and_weight)
                try:
                    if (re.search('\d', assessment_table[i][index_mark_column])):
                            assessment_and_weight.append((assessment_table[i][index_name_column], assessment_table[i][index_mark_column]))
                except:
                    continue

            if len(assessment_and_weight) > 0:
                final_list = []
                for tup in assessment_and_weight:
                    if "\n" in tup[0] or tup[1]: # If either assessment name or weight contains new line, split them and create pairs because they are likely to be separate assessments, otherwise keep the tuple as is
                        col1 = tup[0].split('\n')
                        col2 = tup[1].split('\n')
                        final_list.extend(zip(col1, col2)) 
                    else:
                        final_list.append(tup)

                assessment_and_weight = final_list
                exclude_keywords = {"100"}
                
                # Remove any entries that contain exclude keywords in assessment name or are equal to 100 in weight
                filtered = [item for item in assessment_and_weight if not any(keyword in item[1].lower() for keyword in exclude_keywords)]
                filtered = [item for item in filtered if item[1] != 100 and item[1] != "100"]

                return filtered
    return None



def get_assessment_methods_and_weight(doc: pymupdf.Document) -> list[tuple[str, str]]:
    """Returns assessment methods along with their corresponding weightage, given the path of file for the course syllabus"""
    # doc = pymupdf.open(filePath)
    
    assessment_and_weight = []
    for page in doc:
        listOfText = page.get_text("text")
        # print(listOfText)
        
        # Find assessment and weight from tables first and return if found
        tables = page.find_tables()
        if tables:
            assessment_weight_from_tables = get_assessment_weight_from_table(tables)
            if assessment_weight_from_tables:
                return assessment_weight_from_tables

        # lines = listOfText.split('\n')
        regex = re.compile(r'(?P<label>[A-Z][\w\s\[\]\-/–():.&@%*=]*?)[:.…\s]*?(\d+(?:\.\d+)?)\s*(?:%|points|pts)(?=\s|$)') # Matches patterns like "Midterm: 30%" or "Final Exam - 40 points"
        regexWithBrackets = re.compile(r'^(?P<label>[A-Z][\w\s\[\]\-/–():.&%]*?)\s*\(\s*(?P<value>\d+)%\s*\)\s*$', re.MULTILINE) # Matches patterns like "Midterm (30%)" or "Final Exam (40%)"
        allMatches = re.findall(regex, listOfText) 
        allMatchesWithBrackets = re.findall(regexWithBrackets, listOfText)
        results = []
        
        
        if len(allMatches) > 0:
            is_sum_100 = sum(float(points) for assessment, points in allMatches) >= 100
            if is_sum_100 and len(allMatches) > 1:
                cleaned_assessment = clean_assessment_and_weights(allMatches)
                if sum(float(points) for assessment, points in cleaned_assessment) >= 100:
                    return cleaned_assessment
                else:
                    assessment_and_weight.extend(cleaned_assessment)
                    continue

            if clean_and_validate_assessment_weight_match(allMatches):
                allMatches = clean_assessment_and_weights(allMatches)
                assessment_and_weight.extend(allMatches)

        if len(allMatchesWithBrackets) > 0:
            is_sum_100 = sum(float(points) for assessment, points in allMatchesWithBrackets) >= 100
            if is_sum_100 and len(allMatchesWithBrackets) > 1:
                cleaned_assessment = clean_assessment_and_weights(allMatchesWithBrackets)
                if sum(float(points) for assessment, points in cleaned_assessment) >= 100:
                    return cleaned_assessment
                else:
                    assessment_and_weight.extend(cleaned_assessment)
                    continue

            # print(listOfText)
            if clean_and_validate_assessment_weight_match(allMatchesWithBrackets):
                assessment_and_weight.extend(allMatchesWithBrackets)

        lowerListOfText = listOfText.lower()
        if len(assessment_and_weight) == 0 and 'component' in lowerListOfText and 'percentage' in lowerListOfText:
            assessment_and_weight = get_assessment_and_weight_separated_in_different_lines(lowerListOfText)
            break
    cleaned_assessment = clean_assessment_and_weights(assessment_and_weight)
    return cleaned_assessment

def encode_assessment_and_weight(assessment_and_weights: list[tuple[str, str]]) -> list[tuple[str, int | float]]:
    """ Returns encoded assessments and weight lsit, where weights are either integer or float """
    
    encodedAssessmentNWeight = []
    for assessmentName, weight in assessment_and_weights:
        match = re.search(r"\d+\.?\d*", weight)
        if match:
            try:
                encodedWeight = float(match.group()) if "." in match.group() else int(match.group())
                encodedAssessmentNWeight.append((assessmentName, encodedWeight))
            except ValueError:
                continue
            except TypeError:
                continue
    return encodedAssessmentNWeight


def get_course_topics(doc: pymupdf.Document, doc_without_header: list[str] ) -> list[str]:

    topic_pages = find_topic_section(doc_without_header) #get pages of where topic section falls
    table_topics = get_topics_from_table(doc, topic_pages) #extract all cells from topic columns
    if(table_topics):
        return clean_topics(table_topics) #clean all the topics (remove ignore_topics)
    

    text_topics = get_topics_from_text(doc_without_header, topic_pages) 
    return clean_topics(text_topics)



def find_topic_section(doc: list[str]) -> list[int]:
    topic_pages = []
    in_section = False
    

    expected_headings = {"schedule of topics", "topics", "course topics", "schedule", "schedule of learning topics",
                        "course schedule", "lecture schedule", "tentative lecture schedule", "tentative schedule",
                        "schedule of topics and assessments", "course contents", "course content", "lecture topics", 
                        "lectures", "weekly schedule", "weekly course schedule", "course outline", "class schedule",
                        "class topics", "lecture outline", "course calendar", "weekly topics", "weekly modules", "modules",
                        "course modules", "units", "course units", "weekly readings and topics", "schedule of classes",
                        "schedule of lectures", "lecture and lab schedule", "course and lab schedule", "topics and schedule",
                        "course topics and schedule", "course calendar"}
    
    stop_headings = {
        "assessment","assessments","assessment of learning","assessments of learning",
        "assessment of student learning","assessment methods","assessment schedule","breakdown of marks","mark breakdown","grade breakdown","graded activities","grading scheme","grading",
        "course grading","course grade","evaluation","evaluations","examinations assignments and grading","examinations","assignments","course assignments","learning materials",
        "course materials","learning materials and technology requirements","course materials and learning resources","course structure & learning materials","learning resources",
        "course policies","university policies","academic integrity","student support","student wellbeing","academic accommodations","accessibility","communication protocols","contacts",
        "contact","teaching team","instructional staff","copyright","learning objectives","learning outcomes","course learning objectives","course learning outcomes",
        }

    
    
    for page_index, page_text in enumerate(doc):
        lines = page_text.split("\n")

        if not in_section:
            for line in lines:
                clean_line = line.strip().lower().rstrip(":")
                clean_line = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line)

                # some syllabi prefix section headings with course info such as
                # LAND 304: Tentative Lecture Schedule Check both the full line and
                # the text after the colon so prefixed headings can still match our known
                # topic heading names

                heading_candidates = {clean_line}

                if ":" in clean_line:
                    heading_candidates.add(clean_line.split(":", 1)[1].strip())

                if heading_candidates & expected_headings:
                    in_section = True
                    topic_pages.append(page_index)
                    break

            continue

        # already in topics section
        topic_pages.append(page_index)

        # after the topic section starts, keep adding pages until a known next section heading is found.
        for line in lines:
            clean_line = line.strip().lower().rstrip(":")
            clean_line = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line) 

            if clean_line in stop_headings:
                return topic_pages

        
    return topic_pages


def is_section_boundary(line: str, stop_headings: set[str], topic_headings: set[str]) -> bool:
    stripped_line = line.strip()
    clean_line = stripped_line.lower().rstrip(":")
    clean_line = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line)

    if not clean_line:
        return False
    if clean_line in topic_headings:
        return False
    if clean_line in stop_headings:
        return True

    clean_without_number = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line).rstrip(":")
    if clean_without_number in stop_headings:
        return True

    words = clean_without_number.split()
    if len(words) > 6:
        return False

    if stripped_line.isupper() and len(words) >= 1:
        return True

    if re.match(r"^\d+(\.\d+)*[.)]?\s+[A-Z][A-Za-z&/ -]+$", stripped_line):
        return True

    return False


def get_topics_from_table(doc: pymupdf.Document, topic_pages: list[int]) -> list[str]:
    topics = []
    previous_topic_column_indexes = []

    topic_column_headings = {
        "topic","topics","lecture","lecture topic","lecture topics","lab topic","lab topics",
        "class topic","class topics","course topic","course topics","module topics","weekly topics","weekly topic"
    }
    title_column_headings = {"title", "name", "topic name", "topic title", "topics title"}
    schedule_column_headings = {"week", "date", "dates", "module", "unit", "lecture"}
    ignored_column_headings = {"reading","readings","readings deadlines","readings and deadlines","deadline","deadlines","due date","assessment","assessments",
        "activity","activities","mark","marks","weight","weight %","percentage","%","number","#","week",}

    for page_index in topic_pages: 
        if page_index < 0 or page_index >= len(doc):
            continue  

        tables = doc[page_index].find_tables()
        if not tables:
            continue

        for table in tables.tables:
            extracted_table = table.extract()
            if not extracted_table or len(extracted_table) < 2:
                continue

            cleaned_table = []
            for row in extracted_table: #extract and clean the table
                row_has_content = False
                cleaned_row = []

                for cell in row:
                    if isinstance(cell, str):
                        cleaned_cell = cell.strip()
                    else:
                        cleaned_cell = ""

                    if cleaned_cell:
                        row_has_content = True

                    cleaned_row.append(cleaned_cell)

                if row_has_content:
                    cleaned_table.append(cleaned_row)

            if len(cleaned_table) < 2:
                continue

            header = []
            for cell in cleaned_table[0]:
                header.append(normalize_table_heading(cell)) #get header from cleaned table

            header_set = set(header)
            has_topic_header = bool(header_set & topic_column_headings)

            if header_set & ignored_column_headings and not header_set & topic_column_headings: #if header has ignored columns and not any topic columns, skip
                continue

            topic_column_indexes = []
            for index, heading in enumerate(header): #get column indexes for topic columns
                if heading in topic_column_headings:
                    topic_column_indexes.append(index)


            title_column_indexes = []
            for index, heading in enumerate(header): #get column indexes for title columns
                if heading in title_column_headings:
                    title_column_indexes.append(index)


            if title_column_indexes and header_set & (schedule_column_headings | topic_column_headings):
                for title_column_index in title_column_indexes:
                    topic_column_indexes.append(title_column_index) #if there is a title column and also schedule/topic column, the title column is likely the topic name, so add it to topic indexing
            #we would treate the titel_column like a topic column but it would still end up extracting all columns (including the topic column that only has numbers), so clean_topics() must take care of this

            filtered_topic_column_indexes = []
            for index in topic_column_indexes:  #remove any ignored column headings from chosen topic columns
                if header[index] not in ignored_column_headings: #(we could switch to a different approach where we remove the ones not appearing in pre selected heading columns )
                    filtered_topic_column_indexes.append(index)


            topic_column_indexes = filtered_topic_column_indexes

            # Some continued tables keep the same columns but lose the header row on the next page/table fragment. so we can reuse the topic columns from the previous page
            if not topic_column_indexes and previous_topic_column_indexes:
                topic_column_indexes = previous_topic_column_indexes

            if not topic_column_indexes:
                continue

            previous_topic_column_indexes = topic_column_indexes

            if has_topic_header:
                rows_to_process = cleaned_table[1:]  #if there is a header row, we processes everything but the header, but if there isnt, we process every row
            else:
                rows_to_process = cleaned_table

            for row in rows_to_process:
                for topic_column_index in topic_column_indexes:
                    if topic_column_index >= len(row):
                        continue

                    cell = row[topic_column_index].strip()
                    if not cell:
                        continue

                    topics.extend(split_topic_cell(cell))

    return topics


def normalize_table_heading(heading: str) -> str:
    heading = heading.strip().lower()
    heading = heading.replace("&", "and")
    heading = re.sub(r"[%()*:]", "", heading)
    heading = re.sub(r"\s+", " ", heading)
    return heading.strip()


def split_topic_cell(cell: str) -> list[str]:
    split_topics = []

    for item in cell.split("\n"):
        item = item.strip()
        if not item:
            continue

        no_labs_match = re.match(r"^no labs?\s*\((.+)\)$", item, re.IGNORECASE)
        if no_labs_match:
            split_topics.append(no_labs_match.group(1).strip())
            continue

        split_topics.append(item)

    return split_topics


def clean_topics(topics: list[str]) -> list[str]:
    cleaned_topics = []
    ignore_topics = {"no lab", "no labs", "mid term", "mid term 1", "mid term 2", "no class", "class canceled",
                     "final exam", "final", "tba", "getting started", "no readings", "no assignments", "review",
                     "final review", "mid term review", "midterm review", "midterm", "midterm 1", "midterm 2", "midterm exam",
                     "review session", "final exam tba", "none", "canceled", "quiz 1", "quiz 2", "quiz 3", "quiz 0", "quiz 4", "quiz 5",
                     "quiz 6", "assignment", "due", "course review", "in-class practice", "in-class review","exam", "test", "reading week",
                     "reading break","term break","spring break","statutory holiday","holiday","thanksgiving","remembrance day","labour day",
                    "make-up class", "make up class", "project presentations", "case study presentations", "assignment due", "proposal due",
                     "final project due", "no lecture", "no lecture - holiday", "no tutorial", "no tutorials", "wrap up",
                     "reading break - no class", "reading break no class", "wrap-up and review", "wrap up and review", "reading"}
    
    for topic in topics:
        topic = topic.strip()
        topic = only_bullet_pattern.sub("", topic).strip()
        topic = topic.replace("–", "-").replace("—", "-")
        topic = topic.rstrip("*").strip() #test syllabi were outputted with topics that had "*" attatched to the end, this is why this is here

        if not topic:
            continue
        if re.fullmatch(r"[A-Za-z]?\d+(\.\d+)*[.)]?", topic):
            continue
        if re.fullmatch(r"\d+(\.\d+)*[.)]?", topic): #remove if toppic is a number like value
            continue 

        lower_topic = topic.lower()
        lower_topic = lower_topic.replace("–", "-").replace("—", "-") #there are diff dashes that python treats differently
        
        lower_topic = re.sub(r"\s+", " ", lower_topic).strip()
        if any(ignore_topic in lower_topic for ignore_topic in ignore_topics):
            continue
        topic = re.sub(r"\s*\([^)]*(dr\.|instructor|ta|teaching assistant|prof|professor|teacher)[^)]*\)\s*$", "", topic, flags=re.IGNORECASE).strip() #strips instructor-style parenthesis
        if topic in cleaned_topics:
            continue
        
        cleaned_topics.append(topic)


    return cleaned_topics  


def get_topics_from_text(doc: list[str], topic_pages: list[int]) -> list[str]:
    topics = []
    expected_headings = {"schedule of topics", "topics", "course topics", "schedule", "schedule of learning topics",
                        "course schedule", "lecture schedule", "tentative lecture schedule", "tentative schedule",
                        "schedule of topics and assessments", "course contents", "course content", "lecture topics", 
                        "lectures", "weekly schedule", "weekly course schedule", "course outline", "class schedule",
                        "class topics", "lecture outline", "course calendar", "weekly topics", "weekly modules", "modules",
                        "course modules", "units", "course units", "weekly readings and topics", "schedule of classes",
                        "schedule of lectures", "lecture and lab schedule", "course and lab schedule", "topics and schedule",
                        "course topics and schedule", "course calendar"}
    ignored_lines = {"week", "weeks", "date", "dates", "day", "days", "topic", "topics", "title", "name", "lecture", "lectures", "module", "modules",
                    "unit", "units", "class", "classes", "session", "sessions", "reading", "readings", "required reading", "required readings",
                    "recommended reading", "recommended readings", "assignment", "assignments", "deadline", "deadlines", "due", "due date", "due dates", 
                    "quiz", "quizzes", "exam", "exams", "test", "tests", "assessment", "assessments", "activity", "activities", "lab", "labs", "tutorial", 
                    "tutorials", "workshop", "workshops", "in-class work", "in class work", "who", "instructor", "location", "room", "notes", "comments", 
                    "description", "overview"}
    stop_headings = {
    "assessment",
    "assessments", "communication protocols", "academic and learning resources", "netiquette expectations", "universities policies", "university policies", "academic integrity"
    "assessment of learning",
    "assessments of learning","assessment of student learning","assessment methods","assessment schedule","breakdown of marks","mark breakdown","grade breakdown",
    "graded activities","grading scheme","grading","course grading","course grade","evaluation","evaluations","examinations assignments and grading","examinations",
    "assignments","course assignments","learning materials","course materials","learning materials and technology requirements","course materials and learning resources",
    "course structure & learning materials","learning resources","required materials","required readings","recommended readings","textbook","textbooks","course policies",
    "university policies","academic integrity","student support","student wellbeing","academic accommodations","accessibility","communication protocols","contacts",
    "contact","teaching team","instructional staff","copyright","learning objectives","learning outcomes","course learning objectives","course learning outcomes",
    }
    


    started = False #to indicate when to start extracting topic lines since this method can start earlier than it is supposed to

    for page_count, page_index in enumerate(topic_pages):
        if page_index < 0 or page_index >= len(doc):
            continue

        lines = doc[page_index].split("\n")

        if page_count > 0:
            started = True

        for line in lines:
            line = line.strip()

            if not line:
                continue

            clean_line = line.lower().rstrip(":")

            # the first topic page can contain earlier sections above the schedule heading sp
            # only start text extraction once the topic heading itself is reached.
            heading_line = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line)
            heading_candidates = {heading_line}
            if ":" in heading_line:
                heading_candidates.add(heading_line.split(":", 1)[1].strip())

            if not started: #if we have not reached the schedule heading yet, keep skipping lines but once we find the heading we can start extracting
                #this would prevent early extraction of non-topics
                if heading_candidates & expected_headings:
                    started = True
                continue
            if is_section_boundary(line, stop_headings , expected_headings):
                return topics #once text extraction has started, this will stop it if we hit a later section heading

            if clean_line in ignored_lines:
                continue

            if only_bullet_pattern.match(line):
                topic = only_bullet_pattern.sub("", line).strip() #if bullet/numbered lines/points, extract each line 
                topics.append(topic)
                continue

            module_match = re.match(r"^(module|week|unit|lecture)\s+\d+[.:–—-]\s*(.+)$", line, re.IGNORECASE ) #extract module/week lines 

            if module_match:
                topics.append(module_match.group(2).strip())
                continue

            date_topic_match = re.match(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2}[,:]?\s+(.+)$", line, re.IGNORECASE) #extract date + topic lines

            if date_topic_match:
                topics.append(date_topic_match.group(2).strip())
                continue

            words = line.split()
            if 3 <= len(words) <= 12 and not line.endswith("."): #extract topic looking plain lines
                topics.append(line)

    return topics



def get_course_materials(doc: pymupdf.Document, doc_without_header: list[str]) -> list[dict]:
    material_pages = find_material_section(doc_without_header)

    text_materials = get_materials_from_text(doc_without_header, material_pages)
    if(text_materials):
        return clean_materials(text_materials)
    
    return []
    # return  clean_materials(get_materials_from_table(doc, material_pages))
    # tables for materials is very rare - so this is an optional add on for extreme edge cases



def find_material_section(doc: list[str]) -> list[int]:
    pages = []
    in_section = False
    expected_headings = {"learning materials", "course materials", "required readings", "recommended readings","textbook","textbooks",
    "required textbook","required textbooks","course resources","learning resources", "materials and resources","textbook and references","course materials and learning resources",
    "learning materials and technology requirements", "course structure and learning materials", "course references", "optional readings", "optional textbook",
    "optional textbooks", "optional resources","required materials","required readings","recommended readings","textbook","textbooks", "learning materials", "course materials",
    "learning materials and technology requirements", "course materials and learning resources", "learning resources",}
    stop_headings = {
        "assessment","assessments","assessment of learning","assessments of learning",
        "assessment of student learning","assessment methods","assessment schedule","breakdown of marks","mark breakdown","grade breakdown","graded activities","grading scheme","grading",
        "course grading","course grade","evaluation","evaluations","examinations assignments and grading","examinations","assignments","course assignments","learning materials","technology requirements",
        "course policies","university policies","academic integrity","student support","student wellbeing","academic accommodations","accessibility","communication protocols","contacts",
        "contact","teaching team","instructional staff","copyright","learning objectives","learning outcomes","course learning objectives","course learning outcomes",
        "schedule of topics", "topics", "course topics", "schedule", "schedule of learning topics","course schedule", "lecture schedule", "tentative lecture schedule", "tentative schedule",
        "schedule of topics and assessments", "course contents", "course content", "lecture topics", "weekly schedule", "weekly course schedule", "course outline", "class schedule",
        "class topics", "lecture outline", "course calendar", "weekly topics", "weekly modules", "modules","course modules", "units", "course units", "weekly readings and topics", "schedule of classes",
        "schedule of lectures", "lecture and lab schedule", "course and lab schedule", "topics and schedule","course topics and schedule", "course calendar"}
    
    #clean each line
    for page_index, page_text in enumerate(doc):
        lines = page_text.split("\n")

        if not in_section:
            for line in lines:
                clean_line = line.strip().lower().rstrip(":")
                clean_line = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line)

                # some syllabi prefix section headings with course info such as
                # LAND 304: Tentative Lecture Schedule Check both the full line and
                # the text after the colon so prefixed headings can still match our known
                # material heading names

                heading_candidates = { clean_line }

                if ":" in clean_line:
                    heading_candidates.add(clean_line.split(":", 1)[1].strip())

                if heading_candidates & expected_headings:
                    in_section = True
                    pages.append(page_index)
                    break

            continue

        # already in materials section
        pages.append(page_index)

        # after the materials section starts, keep adding pages until a known next section heading is found.
        for line in lines:
            clean_line = line.strip().lower().rstrip(":")
            clean_line = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line) 

            if clean_line in stop_headings:
                return pages
    return pages


def get_materials_from_text(doc: list[str], pages: list[int]) -> list[dict]:
    materials = []
    expected_headings = {"learning materials", "course materials", "required readings", "recommended readings","textbook","textbooks",
    "required textbook","required textbooks","course resources","learning resources", "materials and resources","textbook and references","course materials and learning resources",
    "learning materials and technology requirements", "course structure and learning materials", "course references", "optional readings", "optional textbook",
    "optional textbooks", "optional resources","required materials","required readings","recommended readings","textbook","textbooks", "learning materials", "course materials",
    "learning materials and technology requirements", "course materials and learning resources", "learning resources","recommended literature sources", "recommended literature resources"}

    stop_headings = {"assessment","assessments","assessment of learning","assessments of learning",
    "assessment of student learning","assessment methods","assessment schedule","breakdown of marks","mark breakdown","grade breakdown","graded activities","grading scheme","grading",
    "course grading","course grade","evaluation","evaluations","examinations assignments and grading","examinations","assignments","course assignments","technology requirements",
    "course policies","university policies","academic integrity","student support","student wellbeing","academic accommodations","accessibility","communication protocols","contacts",
    "contact","teaching team","instructional staff","copyright","learning objectives","learning outcomes","course learning objectives","course learning outcomes",
    "schedule of topics", "topics", "course topics", "schedule", "schedule of learning topics","course schedule", "lecture schedule", "tentative lecture schedule", "tentative schedule",
    "schedule of topics and assessments", "course contents", "course content", "lecture topics", "weekly schedule", "weekly course schedule", "course outline", "class schedule",
    "class topics", "lecture outline", "course calendar", "weekly topics", "weekly modules", "modules","course modules", "units", "course units", "weekly readings and topics", "schedule of classes",
    "schedule of lectures", "lecture and lab schedule", "course and lab schedule", "academic conduct", "academict misconduct",}

    ignore_lines = {"none", "n/a", "na", "not applicable", "supplies needed", "technology requirements", "technology", "learning materials", "course materials", "other course materials", "course resources", "learning resources",
    "textbook and readings", "textbook and references", "required textbooks", "required textbook", "recommended readings", "recommended literature sources", "optional resources", "digital resources", 
    "course website", "canvas", "course structure", "learning activities", "assessment", "assessments", "assessments of learning", "assessment of learning", "graded activities", "marks", "weight",
    "course policies", "university policies", "academic integrity", "academic accommodations", "student support", "student wellbeing", "copyright", "communication protocols", "teaching team",
    "instructional staff", "contact", "contacts", "office hours", "schedule", "schedule of topics", "course schedule", "lecture schedule", "tentative schedule", "topics", "week", "date", "lecture",
    "lab", "assignment", "assignments", "quiz", "quizzes", "exam", "exams", "midterm", "final exam", "participation", "students may purchase the textbook through the ubc bookstore", "additional readings will be provided through canvas",
    "additional articles, multimedia resources, case studies, and readings will be provided through canvas modules", "all updated course information will be available through the canvas course website",
    "only registered students will have access to the course materials hosted through canvas", "students should have access to a computer or tablet capable of accessing canvas", "there are no mandatory textbook requirements for this course",
    "the following are optional textbooks and resources for review", "students experiencing difficulties with course technologies assignments or course materials are encouraged to contact the teaching team early in the term",
    "course materials are intended only for students enrolled in the course and may not be redistributed without permission", "all materials in this course are the intellectual property of the course instructor or licensed for educational use",
    "laptop", "mobile device", "tablet", "paper", "calculator", "wifi", "internet", "technology"}

    material_labels = {
            "required textbook","required textbooks","optional textbook","optional textbooks","optional articles","optional article","required readings",
            "required reading","optional reading","optional readings","optional text for lectures","optional text for labs","digital resources","course materials",
            "other course materials","recommended literature sources","textbook and references","required documentary / video content","podcast and audio media",
            "websites and online articles","recomended literature sources","learning materials","podcast","podcast and audio media","online articles","websites and online articles",
            "required and optional readings"
        }
    material_keywords = {
    "textbook", "edition", "readings", "reading", "slides", "canvas","software", "arcgis", "qgis", "calculator", "journal articles",
    "case studies", "documentary", "video", "podcast", "website","portal", "articles", "article", "book"
}
    citation_pattern = re.compile(r"^[A-Z][A-Za-z'’.-]+,\s+[A-Z](?:\.\s*)?(?:&\s+[A-Z][A-Za-z'’.-]+,\s+[A-Z](?:\.\s*)?)?\s+\d{4}\.\s+.+\.\s+.+\.?$") #regex for citation patterns

    started = False
    current_description = ""
    current_material_name = ""
    

    for page_count, page_index in enumerate(pages):
        if page_index < 0 or page_index >= len(doc):
            continue

        lines = doc[page_index].split("\n")

        if page_count > 0:
            started = True

        for line in lines:
            line = line.strip()

            if not line:
                continue

            clean_line = line.lower().rstrip(":")

            # the first material page can contain earlier sections above the schedule heading sp
            # only start text extraction once the heading itself is reached.
            heading_line = re.sub(r"^\d+(\.\d+)*[.)]?\s*", "", clean_line)
            heading_candidates = {heading_line}
            if ":" in heading_line:
                heading_candidates.add(heading_line.split(":", 1)[1].strip())

            if not started: #if we have not reached the module heading yet, keep skipping lines but once we find the heading we can start extracting
                #this would prevent early extraction of non-materials
                if heading_candidates & expected_headings:
                    started = True
                continue
            if is_section_boundary(line, stop_headings , expected_headings):
                return materials #once text extraction has started, this will stop it if we hit a later section heading
            
            if clean_line in material_labels:
                current_description = line.rstrip(":").strip()
                continue

            if clean_line in ignore_lines:
                continue


            ### bullet points extraction
            if only_bullet_pattern.match(line):
                material_name = only_bullet_pattern.sub("", line).strip()
                clean_material_name = material_name.lower()
                clean_material_name = clean_material_name.replace("–", "-").replace("—", "-")
                clean_material_name = re.sub(r"\s+", " ", clean_material_name).strip()
                if clean_material_name in ignore_lines: #optionally change this to just any ignore_lines apearing anywhere in material name (less strict)
                    continue

                if ":" in material_name:
                    name, description = material_name.split(":", 1)
                    name = name.strip()
                    description = description.strip()

                    label_before_col = name.lower() #var to check if the left side or gith side of te ":" has the name or description

                    if(label_before_col in material_labels):
                        materials.append({
                            "name": description,
                            "type": infer_material_type(description, name),
                            "description": name,
                        })
                        continue

                    if(label_before_col not in material_labels):
                        materials.append({
                            "name": name,
                            "type": infer_material_type(name, description),
                            "description": description,
                        })
                        continue


                if citation_pattern.match(material_name): # likely a textbook citation
                    if current_description == "":
                        current_description = "text for course"

                    current_material_name = material_name
                    materials.append({
                        "name": current_material_name,
                        "type": infer_material_type(current_material_name, current_description),
                        "description": current_description,
                    })

                    continue

                if current_description == "":
                    current_description = "resource for course"

                materials.append({
                    "name": material_name,
                    "type": infer_material_type(material_name, current_description),
                    "description": current_description,
                })
                continue
            ### end of bullet points extraction


            #handles things like "required textbook:", or "the course textbook is..."
            textbook_match = re.match(r"^(the course textbook is|required textbook)\s*:?\s*(.+)$", line, re.IGNORECASE)
            if textbook_match:
                description = textbook_match.group(1).strip()
                name = textbook_match.group(2).strip() 

                materials.append({
                    "name": name,
                    "type": infer_material_type(name, description),
                    "description": description,
                })
                continue

            required_textbook_match = re.match(r"^required textbook\s*:?\s*(.+?)(?:\s+additional readings.*)?$", line, re.IGNORECASE)
            if required_textbook_match:
                name = required_textbook_match.group(1).strip()

                materials.append({
                    "name": name,
                    "type": infer_material_type(name, "Required textbook"),
                    "description": "Required textbook",
                })

                if "additional readings" in clean_line:
                    materials.append({
                        "name": "Additional readings and tutorial resources will be posted on Canvas.",
                        "type": "reading",
                        "description": "Textbook and References",
                    })
                continue

            if ":" in line: #handles label + material lines like "Required readings: article title"
                name, description = line.split(":", 1)
                name = name.strip()
                description = description.strip()

                label_before_col = name.lower() #checks if the left side of the colon is a label instead of the material name

                if name and description and any(keyword in clean_line for keyword in material_keywords):
                    if label_before_col in material_labels:
                        materials.append({
                            "name": description,
                            "type": infer_material_type(description, name),
                            "description": name,
                        })
                        continue

                    materials.append({
                        "name": name,
                        "type": infer_material_type(name, description),
                        "description": description,
                    })
                    continue
            
            if citation_pattern.match(line): #handles citation looking lines
                if current_description == "":
                    current_description = "text for course"
                
                materials.append({
                    "name": line,
                    "type": infer_material_type(line, current_description),
                    "description": current_description,
                })

                continue

            if any(keyword in clean_line for keyword in material_keywords): #handles non-citation looking resources
                if current_description == "":
                    current_description = "resource for course"

                materials.append({
                    "name": line,
                    "type": infer_material_type(line, current_description),
                    "description": current_description,
                })
                continue

    return materials

def infer_material_type(name: str, description: str) -> str:
    material_types = [
        "textbook","software","podcast","documentary","video","article","case study","website",
        "online resource","digital resource","lecture slide","slides","reading","book","movie","calculator",
        "equipment",]
    citation_pattern = re.compile(r"^[A-Z][A-Za-z'’.-]+,\s+[A-Z](?:\.\s*)?(?:&\s+[A-Z][A-Za-z'’.-]+,\s+[A-Z](?:\.\s*)?)?\s+\d{4}\.\s+.+\.\s+.+\.?$") #regex for citation patterns
    
    is_citation = citation_pattern.match(name) or citation_pattern.match(description)
    
    
    name = name.strip().lower()
    description = description.strip().lower()

    if "calculator" in name or "calculator" in description:
        return "equipment"

    for t in material_types:
        if t in name:
            return t
        
        if t in description:
            return t
        
    
    if is_citation: #citation likely are for textbooks
        return "textbook"
    
    return "course resource"
    

def clean_materials(materials: list[dict]) -> list[dict]:


    return []



