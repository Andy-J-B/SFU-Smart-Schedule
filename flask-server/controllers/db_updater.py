# db_updater.py

import re, requests, json

# Timer
import time

# get the start time
st = time.time()

# Import sfu_api functions
from sfu_api import SFUCoursesAPI

# Load dotenv environmental variables
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("supabase_url")
SUPABASE_KEY = os.getenv("supabase_key")

# Supabase connection
import os
from supabase import create_client, Client

url: str = os.environ.get(SUPABASE_URL)
key: str = os.environ.get(SUPABASE_KEY)
# supabase: Client = create_client(url, key)


class SupabaseInserter:
    """
    Class to handle inserting data into the supabase db
    Make the database using the given course options.
    """

    def __init__(self, supabase_client: Client, sfu_data: dict):
        self.supabase = supabase_client
        self.sfu_data = sfu_data
        self.api = SFUCoursesAPI()

    def fetch_and_sync_all(self):
        self.sync_departments()
        for dept_code, courses in self.sfu_data.items():
            print(f"Processing department: {dept_code}")
            # self.sync_department(dept_code)

            course_entries = []
            section_entries = []
            instructor_entries = []
            schedule_entries = []

            for course_number, sections in courses.items():
                for section_id in sections:
                    print(f"Fetching {dept_code} {course_number} {section_id}")
                    section_info = self.api.get_section_info(
                        dept_code, course_number, section_id
                    )

                    # Parse course
                    course_data = self.extract_course_data(
                        section_info, dept_code, course_number
                    )
                    course_entries.append(course_data)

                    # Parse section
                    section_data = self.extract_section_data(
                        section_info, dept_code, course_number, section_id
                    )
                    section_entries.append(section_data)

                    # Parse instructors
                    instructors = self.extract_instructors(
                        section_info, dept_code, course_number, section_id
                    )
                    instructor_entries.extend(instructors)

                    # Parse schedule
                    schedules = self.extract_schedule(
                        section_info, dept_code, course_number, section_id
                    )
                    schedule_entries.extend(schedules)

            self.sync_courses(course_entries)
            self.sync_sections(section_entries)
            self.sync_instructors(instructor_entries)
            self.sync_schedules(schedule_entries)

    def sync_departments(self):
        # Insert to departments table

        # Get current departments from Supabase
        existing = self.supabase.table("departments").select("dept_code").execute()
        existing_depts = {d["dept_code"] for d in existing.data}

        incoming_depts = set(self.sfu_data.keys())

        # Determine new and stale departments
        new_depts = incoming_depts - existing_depts
        stale_depts = existing_depts - incoming_depts

        # Insert new departments
        if new_depts:
            inserts = [{"dept_code": dept} for dept in new_depts]
            self.supabase.table("departments").insert(inserts).execute()

        # Delete stale departments
        if stale_depts:
            for dept in stale_depts:
                self.supabase.table("departments").delete().eq(
                    "dept_code", dept
                ).execute()

        return

    def sync_department(self, dept_code: str):
        # Executes a single insertion if dept_code doesn't exist

        existing = (
            self.supabase.table("departments")
            .select("dept_code")
            .eq("dept_code", dept_code)
            .execute()
        )

        if not existing.data:
            self.supabase.table("departments").insert(
                {"dept_code": dept_code}
            ).execute()

        return

    def sync_course(self, course_entries: list):
        # Insert to courses table

        existing = (
            self.supabase.table("courses")
            .select("id, dept_code, course_number")
            .execute()
        )
        existing_map = {
            (c["dept_code"], c["course_number"]): c["id"] for c in existing.data
        }

        incoming_keys = {(c["dept_code"], c["course_number"]) for c in course_entries}

        # Insert new courses
        new_courses = [
            c
            for c in course_entries
            if (c["dept_code"], c["course_number"]) not in existing_map
        ]
        if new_courses:
            self.supabase.table("courses").insert(new_courses).execute()

        # Delete stale courses
        stale_ids = [
            cid for key, cid in existing_map.items() if key not in incoming_keys
        ]
        for cid in stale_ids:
            self.supabase.table("courses").delete().eq("id", cid).execute()
        return

    def insert_section(self, section_data: dict):
        # insert to sections table
        pass

    def insert_instructors(self, section_data: dict):
        # insert to sections table
        pass

    def insert_schedules(self, section_data: dict):
        # insert to sections table
        pass

    def extract_course_data(self, section_info, dept, course_number):
        return {
            "dept_code": dept,
            "course_number": course_number,
            "title": section_info.get("title"),
            "units": section_info.get("units"),
            "class_number": section_info.get("classNumber"),
            "prerequisites": section_info.get("prerequisites"),
            "corequisites": section_info.get("corequisites"),
            "designation": section_info.get("designation"),
            "short_note": section_info.get("shortNote"),
            "delivery_method": section_info.get("deliveryMethod"),
        }

    def extract_section_data(self, section_info, dept, course_number, section_id):
        return {
            "dept_code": dept,
            "course_id": course_number,
            "section_code": section_id,
            "class_type": section_info.get("classNumber"),
            "associated_class": section_info.get("enrollmentCapacity"),
            "delivery_method": section_info.get("enrollmentTotal"),
        }

    def extract_instructors(self, section_info, dept, course_number, section_id):
        instructors = section_info.get("instructor", [])
        return [
            {
                "dept_code": dept,
                "course_number": course_number,
                "section_id": section_id,
                "name": instructor,
            }
            for instructor in instructors
        ]

    def extract_schedule(self, section_info, dept, course_number, section_id):
        meeting_info = section_info.get("meetingTimes", [])
        return [
            {
                "dept_code": dept,
                "course_number": course_number,
                "section_id": section_id,
                "days": m.get("days"),
                "start_time": m.get("startTime"),
                "end_time": m.get("endTime"),
                "location": m.get("location"),
                "campus": m.get("campus"),
                "schedule_type": m.get("scheduleType"),
            }
            for m in meeting_info
        ]


# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print("Execution time:", elapsed_time, "seconds")
