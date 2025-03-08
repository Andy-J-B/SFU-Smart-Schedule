import pdfplumber
import re, json

laparams_settings = {
    "line_overlap": 0.3,  # Controls how much overlap is considered a single line
    "char_margin": 0.5,  # Merges characters into words if they are close
    "word_margin": 0.1,  # Merges words if they are close
    "line_margin": 0.1,  # Merges text into lines if they are close
    "boxes_flow": 1,  # Controls the detection of text columns
}

with pdfplumber.open("UT.pdf", laparams=laparams_settings) as pdf:
    text = []
    start_of_courses = False

    for page in pdf.pages:
        for line in page.extract_text_lines():

            # Find which major
            if line["text"].strip().startswith("Major in "):
                major = line["text"]

            # Find which lines are courses
            if line["text"].strip().startswith("Attempted"):
                start_of_courses = True
                continue
            elif start_of_courses and line["text"].startswith("Term"):
                start_of_courses = False
            if line["text"] and start_of_courses and len(line["text"]) > 3:
                text.append(line["text"])

    courses = "\n".join(text)

# print(courses)
# print(major)


def parse_course_data(text_list: list) -> dict:
    """
    Parse course data obtained from transcript PDF.
    Returns a dictionary with each course taken.

    Dictionary structure:
    {
        key: {
            "course_department": <string> (All Caps),
            "course_number": <int>,
            "course_name": <string>,
            "units_attempted": <int>,
            "units_completed": <int>,
            "grade": <string> or None,
            "grade_points": <float>,
            "class_average": <string> or None,
            "class_enrollment": <int>
        },
        ...
    }
    """

    course_dict = {}

    for key, course in enumerate(text_list):
        course_list = extract_course_info(course)

        # Unpacking values from course_list
        (
            course_department,
            course_number,
            course_name,
            units_attempted,
            units_completed,
            *rest,
        ) = course_list

        # Check for missing grade case
        if rest[-2] == "-":
            grade, class_average = None, None
            grade_points, class_enrollment = rest[0], rest[2]
        else:
            grade, grade_points, class_average, class_enrollment = rest

        # Populate dictionary
        print(course_list, class_enrollment, grade_points)
        course_dict[key] = {
            "course_department": course_department,
            "course_number": course_number,
            "course_name": course_name,
            "units_attempted": float(re.sub(r"[^\d.]", "", units_attempted)),
            "units_completed": float(re.sub(r"[^\d.]", "", units_completed)),
            "grade": grade,
            "grade_points": float(re.sub(r"[^\d.]", "", grade_points)),
            "class_average": class_average,
            "class_enrollment": int(re.sub(r"[^\d.]", "", class_enrollment)),
        }

    return course_dict


def extract_course_info(s):
    # Extract first 2 : department and number
    first_parts = s.split(" ", 2)

    # Extract last 6 : units attempted, units completed, grade, grade points, average, enrollment
    last_parts = first_parts[-1].rsplit(" ", 6)

    final_course_list = first_parts[:2] + last_parts

    if final_course_list[-2] == "-":

        final_course_list = (
            first_parts[:2]
            + [final_course_list[2] + " " + final_course_list[3]]
            + final_course_list[4:]
        )

    return final_course_list


course_data_dict = parse_course_data(text)

# Convert Python to JSON
json_object = json.dumps(course_data_dict, indent=4)

# Print JSON object
print(json_object)
