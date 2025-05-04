# sfu_api.py

# Logic for fetching courses from API
import re, requests, json
from testing import timer


class SFUCoursesAPI:
    def __init__(
        self, base_url: str = "http://www.sfu.ca/bin/wcm/course-outlines?2025/spring"
    ):

        # URL for departments in this semester
        self.base_url: str = base_url
        self.excluded_departments = {
            "GERO",
            "LBST",
            "PLAN",
            "ALS",
            "APMA",
            "ARAB",
            "CENV",
            "DMED",
            "EDPR",
            "FAL",
            "FAN",
            "FASS",
            "GERM",
            "GRAD",
            "GRK",
            "INS",
            "ITAL",
            "LBRL",
            "LS",
            "NEUR",
            "NUSC",
            "ONC",
            "PERS",
            "PLCY",
            "PORT",
            "SD",
            "SDA",
            "SPAN",
            "TEKX",
            "UGRAD",
            "URB",
            "WS",
            "WKTM",
            "WDA",
        }

    @timer
    def get_departments(self) -> list:
        """
        Send Get request to SFU Courses API to
        fetch course departments listed for this semester.

        Returns the list of departments in form :
        [<string>, <string>, ...]
        """

        try:
            response = requests.get(self.base_url)
            response.raise_for_status()  # Raise an error for HTTP errors

            department_list = [
                department["text"]
                for department in response.json()
                if department["text"] not in self.excluded_departments
            ]
            return department_list
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    @timer
    def get_courses(self) -> dict:
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
        departments_list = self.get_departments()
        sfu_courses = {}
        for department in departments_list:
            try:
                response = requests.get(self.base_url + "/" + department)
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
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # Just skip and move on
                    # print(f"404 Not Found for {department}, skipping.")
                    continue
                else:
                    # print(f"HTTP error for {department}: {e}")
                    return {"error": str(e)}

        return sfu_courses

    @timer
    def get_course_sections(self) -> dict:
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

        course_dict = self.get_courses()

        for department, courses in course_dict.items():
            course_section_dict = {}
            # if department != "CMPT":
            #     course_dict[department] = course_section_dict
            #     continue
            for course in courses:
                response = requests.get(
                    self.base_url + "/" + department + "/" + course["text"]
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
        # same logic...

    @timer
    def get_course_outlines(self) -> dict:
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

        course_dict = self.get_course_sections()

        for department, courses in course_dict.items():
            course_section_dict = {}
            # if department != "CMPT":
            #     course_dict[department] = course_section_dict
            #     continue

            for course in courses:
                response = requests.get(self.base_url + "/" + department + "/" + course)
                sections = response.json()

                grouped_sections = []

                for section in sections:
                    if response.status_code == 404:
                        continue

                    # No need to associate here, we alrdy have it in db

                    # associated_number = section["associatedClass"]
                    # if associated_number not in grouped_sections:
                    #     grouped_sections[associated_number] = []

                    # grouped_sections[associated_number].append(section)
                    grouped_sections.append(section["value"])

                course_section_dict[course] = grouped_sections
            course_dict[department] = course_section_dict

        return course_dict

    @timer
    def get_section_info(self, dept: str, course: str, section: str) -> dict:
        """
        Fetches detailed info for a specific section of a course.

        Args:
            dept (str): Department code (e.g., "CMPT")
            course (str): Course number (e.g., "225")
            section (str): Section ID (e.g., "D100")

        Returns:
            dict: Section info or {} if request fails
        """

        try:
            url = f"{self.base_url}/{dept}/{course}/{section}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}
