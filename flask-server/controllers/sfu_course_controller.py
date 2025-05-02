# Logic for fetching courses from API

import re, requests, json

# URL for departments in this semester
COURSE_API_URL = "http://www.sfu.ca/bin/wcm/course-outlines?2025/summer"

# URL for courses for this department in this semester


def get_sfu_departments() -> list:
    """
    Send Get request to SFU Courses API to
    fetch course departments listed for this semester.

    Returns the list of departments in form :
    [<string>, <string>, ...]
    """

    try:
        response = requests.get(COURSE_API_URL)
        response.raise_for_status()  # Raise an error for HTTP errors
        department_list = [department["text"] for department in response.json()]
        return department_list
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_sfu_courses() -> dict:
    """
    Send Get request to SFU Courses API to
    fetch courses for each department listed for this semester.

    Returns the dict of courses for each department in form :
    {
        <string (department)> : [
            <dict (course) >
        ]
    }
    """

    # Make sure course numbers are below 500
    departments_list = get_sfu_departments()
    sfu_courses = {}
    for department in departments_list:
        try:
            response = requests.get(COURSE_API_URL + "/" + department)
            response.raise_for_status()  # Raise an error for HTTP errors
            sfu_courses[department] = []

            for course in response.json():
                if int(re.sub(r"[^\d]", "", course["text"])) > 500:
                    continue
                elif "title" in course and (
                    "Practicum" in course["title"]
                    or "Research Project" in course["title"]
                ):
                    continue
                else:
                    sfu_courses[department].append(course)
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    return sfu_courses


def get_course_sections():
    """
    Send Get request to SFU Courses API to
    fetch course sections for each course listed for this semester.

    Returns the dict of course sections for each course in form :

    {
        <string (department)> : {
            <string (course_number)> : [
                <dict (course) >
            ]
        }
    }

    """

    course_dict = get_sfu_courses()

    for department, courses in course_dict.items():
        course_section_dict = {}
        if department != "CMPT":
            course_dict[department] = course_section_dict
            continue
        for course in courses:
            response = requests.get(
                COURSE_API_URL + "/" + department + "/" + course["text"]
            )
            sections = response.json()

            grouped_sections = {}
            for section in sections:
                if response.status_code == 404:
                    continue

                associated_number = section["associatedClass"]
                if associated_number not in grouped_sections:
                    grouped_sections[associated_number] = []

                grouped_sections[associated_number].append(section)
            course_section_dict[course["text"]] = grouped_sections
        course_dict[department] = course_section_dict

    return course_dict


def get_course_outlines():
    """
    Send Get request to SFU Courses API to
    fetch course outlines for each course listed for this semester.
    update or add to the database

    Returns the dict of course sections for each course in form :

    {
        <string (department)> : {
            <string (course_number)> : [
                <dict (course) >
            ]
        }
    }

    """

    course_dict = get_sfu_courses()

    for department, courses in course_dict.items():
        course_section_dict = {}
        if department != "CMPT":
            course_dict[department] = course_section_dict
            continue
        for course in courses:
            response = requests.get(
                COURSE_API_URL + "/" + department + "/" + course["text"]
            )
            sections = response.json()

            grouped_sections = {}
            for section in sections:
                if response.status_code == 404:
                    continue

                associated_number = section["associatedClass"]
                if associated_number not in grouped_sections:
                    grouped_sections[associated_number] = []

                grouped_sections[associated_number].append(section)
            course_section_dict[course["text"]] = grouped_sections
        course_dict[department] = course_section_dict

    return course_dict


def post_db():
    """
    Make the database using the given course options.
    For each section of each course of each department
    Get the course outline, make a database element
    """

    #


def get_db():
    """"""


def update_db():
    """"""


print(get_course_outlines())
