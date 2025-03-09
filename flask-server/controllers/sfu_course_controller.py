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

    """

    return


def get_course_outlines():
    return


# def get_sfu_courses():
#     """Fetch courses from an external API"""
#     try:
#         response = requests.get(COURSE_API_URL)
#         response.raise_for_status()  # Raise an error for HTTP errors
#         return response.json()  # Return JSON response
#     except requests.exceptions.RequestException as e:
#         return {"error": str(e)}


print(get_sfu_courses())
