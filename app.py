"""
CodeCraftHub - Course Tracking REST API

This Flask application provides CRUD operations for courses and stores
course data in a local JSON file named courses.json.

Run the application with:

    python app.py
"""

from datetime import datetime
from pathlib import Path
import json
import os
import re
import threading

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.serving import is_running_from_reloader, make_server, run_simple


# Create the Flask application
app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    """Allow index.html to call the API when it is opened as a file."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, PUT, DELETE, OPTIONS"
    )
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.before_request
def answer_cors_preflight():
    """Answer the browser check that runs before POST and PUT."""
    if request.method == "OPTIONS":
        return "", 204
    return None


@app.get("/")
def home_page():
    """Serve the course page from this same server."""
    return send_from_directory(Path(__file__).parent, "index.html")


# Store courses.json next to this file unless COURSES_FILE points elsewhere.
# A test script can set COURSES_FILE to a copy in /tmp.
DATA_FILE = Path(
    os.environ.get("COURSES_FILE", Path(__file__).parent / "courses.json")
)


# The only status values allowed for a course, in display order.
VALID_STATUSES = (
    "Not Started",
    "In Progress",
    "Completed",
)


# Regular expression for the required YYYY-MM-DD format
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --------------------------------------------------------------------
# Helper functions for reading and writing the JSON file
# --------------------------------------------------------------------

def create_data_file_if_needed():
    """
    Create courses.json automatically if it does not already exist.

    The initial contents are an empty JSON list because courses will be
    stored as a list of objects.
    """
    if not DATA_FILE.exists():
        try:
            DATA_FILE.write_text("[]", encoding="utf-8")
        except OSError as error:
            raise OSError(
                f"Could not create data file: {error}"
            ) from error


def load_courses():
    """
    Read and return all courses from courses.json.

    Returns:
        list: A list of course dictionaries.

    Raises:
        OSError: If the file cannot be read.
        ValueError: If the file contains invalid JSON or invalid data.
    """
    # Make sure the file exists before trying to read it
    create_data_file_if_needed()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            courses = json.load(file)
    except OSError as error:
        raise OSError(
            f"Could not read courses.json: {error}"
        ) from error
    except json.JSONDecodeError as error:
        raise ValueError(
            "courses.json contains invalid JSON"
        ) from error

    # The top-level JSON value must be a list
    if not isinstance(courses, list):
        raise ValueError(
            "courses.json must contain a JSON list"
        )

    return courses


def save_courses(courses):
    """
    Save all courses to courses.json.

    Args:
        courses (list): The list of course dictionaries.

    Raises:
        OSError: If the file cannot be written.
    """
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(courses, file, indent=2)
            file.write("\n")
    except OSError as error:
        raise OSError(
            f"Could not write to courses.json: {error}"
        ) from error


def get_next_course_id(courses):
    """
    Generate the next course ID.

    The first course receives ID 1. Later courses receive the next
    highest available ID.
    """
    if not courses:
        return 1

    existing_ids = [
        course["id"]
        for course in courses
        if isinstance(course.get("id"), int)
    ]

    if not existing_ids:
        return 1

    return max(existing_ids) + 1


def get_current_timestamp():
    """
    Return the current UTC time as an ISO 8601 timestamp.

    Example:
        2026-10-13T12:30:45.123456Z
    """
    return datetime.now().astimezone().isoformat()


# --------------------------------------------------------------------
# Validation helper functions
# --------------------------------------------------------------------

def _non_empty_text_error(value, field_name):
    """Return an error when a text field is missing or blank."""
    if not isinstance(value, str) or not value.strip():
        return f"{field_name} must be a non-empty string"
    return None


def _target_date_error(target_date):
    """Return an error when the target date is not a real YYYY-MM-DD date."""
    if not isinstance(target_date, str):
        return "target_date must be a string in YYYY-MM-DD format"

    if not DATE_PATTERN.fullmatch(target_date):
        return "target_date must use YYYY-MM-DD format"

    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        return "target_date must be a valid calendar date"

    return None


def _status_error(status):
    """Return an error when the status is not one of the allowed values."""
    if status not in VALID_STATUSES:
        return (
            "Invalid status. Status must be one of: "
            + ", ".join(sorted(VALID_STATUSES))
        )
    return None


def validate_course_data(data):
    """
    Validate the fields submitted for a course.

    Returns:
        None if the data is valid.
        A string containing an error message otherwise.
    """
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    required_fields = [
        "name",
        "description",
        "target_date",
        "status",
    ]
    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return "Missing required fields: " + ", ".join(missing_fields)

    return (
        _non_empty_text_error(data["name"], "name")
        or _non_empty_text_error(data["description"], "description")
        or _target_date_error(data["target_date"])
        or _status_error(data["status"])
    )


def build_course_stats(courses):
    """
    Count courses in total and by each allowed status.

    Statuses that are not allowed are included in the total only.
    """
    by_status = {status: 0 for status in VALID_STATUSES}

    for course in courses:
        status = course.get("status")
        if status in by_status:
            by_status[status] += 1

    return {
        "total": len(courses),
        "by_status": by_status,
    }


def find_course(courses, course_id):
    """
    Find one course by ID.

    Returns:
        The matching course dictionary, or None if not found.
    """
    return next(
        (
            course
            for course in courses
            if course.get("id") == course_id
        ),
        None,
    )


def get_json_request_body():
    """
    Safely read the JSON request body.

    Returns:
        A JSON object if the request contains valid JSON.
        None otherwise.
    """
    return request.get_json(silent=True)


# --------------------------------------------------------------------
# REST API endpoints
# --------------------------------------------------------------------

@app.route("/api/courses", methods=["POST"])
def create_course():
    """
    Add a new course.

    Endpoint:
        POST /api/courses
    """
    data = get_json_request_body()

    if data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    validation_error = validate_course_data(data)

    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        courses = load_courses()

        new_course = {
            "id": get_next_course_id(courses),
            "name": data["name"].strip(),
            "description": data["description"].strip(),
            "target_date": data["target_date"],
            "status": data["status"],
            "created_at": get_current_timestamp(),
        }

        courses.append(new_course)
        save_courses(courses)

    except OSError as error:
        return jsonify({
            "error": "File error while saving course",
            "details": str(error),
        }), 500

    except ValueError as error:
        return jsonify({
            "error": "Invalid data file",
            "details": str(error),
        }), 500

    return jsonify(new_course), 201


@app.route("/api/courses", methods=["GET"])
def get_all_courses():
    """
    Return all courses.

    Endpoint:
        GET /api/courses
    """
    try:
        courses = load_courses()

    except OSError as error:
        return jsonify({
            "error": "File error while reading courses",
            "details": str(error),
        }), 500

    except ValueError as error:
        return jsonify({
            "error": "Invalid data file",
            "details": str(error),
        }), 500

    return jsonify(courses), 200


@app.route("/api/courses/stats", methods=["GET"])
def get_course_stats():
    """
    Return how many courses exist, grouped by status.

    Endpoint:
        GET /api/courses/stats
    """
    try:
        courses = load_courses()

    except OSError as error:
        return jsonify({
            "error": "File error while reading courses",
            "details": str(error),
        }), 500

    except ValueError as error:
        return jsonify({
            "error": "Invalid data file",
            "details": str(error),
        }), 500

    return jsonify(build_course_stats(courses)), 200


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """
    Return one course by ID.

    Endpoint:
        GET /api/courses/<id>
    """
    try:
        courses = load_courses()

    except OSError as error:
        return jsonify({
            "error": "File error while reading courses",
            "details": str(error),
        }), 500

    except ValueError as error:
        return jsonify({
            "error": "Invalid data file",
            "details": str(error),
        }), 500

    course = find_course(courses, course_id)

    if course is None:
        return jsonify({
            "error": f"Course with ID {course_id} not found"
        }), 404

    return jsonify(course), 200


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """
    Update an existing course.

    The request must include all required course fields.

    Endpoint:
        PUT /api/courses/<id>
    """
    data = get_json_request_body()

    if data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    validation_error = validate_course_data(data)

    if validation_error:
        return jsonify({"error": validation_error}), 400

    try:
        courses = load_courses()

        course = find_course(courses, course_id)

        if course is None:
            return jsonify({
                "error": f"Course with ID {course_id} not found"
            }), 404

        # Update the editable fields.
        # The ID and created_at timestamp should not change.
        course["name"] = data["name"].strip()
        course["description"] = data["description"].strip()
        course["target_date"] = data["target_date"]
        course["status"] = data["status"]

        save_courses(courses)

    except OSError as error:
        return jsonify({
            "error": "File error while updating course",
            "details": str(error),
        }), 500

    except ValueError as error:
        return jsonify({
            "error": "Invalid data file",
            "details": str(error),
        }), 500

    return jsonify(course), 200


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """
    Delete a course by ID.

    Endpoint:
        DELETE /api/courses/<id>
    """
    try:
        courses = load_courses()

        course = find_course(courses, course_id)

        if course is None:
            return jsonify({
                "error": f"Course with ID {course_id} not found"
            }), 404

        courses.remove(course)
        save_courses(courses)

    except OSError as error:
        return jsonify({
            "error": "File error while deleting course",
            "details": str(error),
        }), 500

    except ValueError as error:
        return jsonify({
            "error": "Invalid data file",
            "details": str(error),
        }), 500

    return jsonify({
        "message": "Course deleted successfully",
        "course": course,
    }), 200


# --------------------------------------------------------------------
# General error handlers
# --------------------------------------------------------------------

@app.errorhandler(404)
def handle_not_found(_error):
    """
    Handle requests to endpoints that do not exist.
    """
    return jsonify({
        "error": "Endpoint not found"
    }), 404


@app.errorhandler(405)
def handle_method_not_allowed(_error):
    """
    Handle requests using an unsupported HTTP method.
    """
    return jsonify({
        "error": "HTTP method not allowed"
    }), 405


@app.errorhandler(500)
def handle_internal_server_error(_error):
    """
    Handle unexpected server errors.
    """
    return jsonify({
        "error": "Internal server error"
    }), 500


def run_on_localhost(listen_port, use_debug):
    """Listen on localhost for both IPv4 and IPv6.

    A browser opens localhost as ::1 first. Binding only 127.0.0.1
    makes that connection fail, so index.html cannot load courses.
    """
    if not use_debug or is_running_from_reloader():
        ipv4_server = make_server("127.0.0.1", listen_port, app, threaded=True)
        threading.Thread(
            target=ipv4_server.serve_forever,
            daemon=True,
        ).start()

    run_simple(
        "::1",
        listen_port,
        app,
        use_reloader=use_debug,
        use_debugger=use_debug,
        threaded=True,
    )


# --------------------------------------------------------------------
# Application startup
# --------------------------------------------------------------------

if __name__ == "__main__":
    # Create courses.json before starting the server.
    # This also means the file exists even before the first API request.
    try:
        create_data_file_if_needed()
    except OSError as error:
        print(f"Startup error: {error}")
        raise SystemExit(1) from error

    # debug=True is useful while learning and developing.
    # Set COURSES_DEBUG=false when another script starts this process.
    port = int(os.environ.get("COURSES_PORT", "5000"))
    debug_value = os.environ.get("COURSES_DEBUG", "true").strip().lower()
    debug = debug_value in {"1", "true", "yes", "on"}
    run_on_localhost(port, debug)
