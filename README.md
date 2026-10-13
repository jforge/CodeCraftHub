# CodeCraftHub

CodeCraftHub is a beginner-friendly learning tracker built with **Python** and the **Flask** web framework.

It provides a REST API for managing courses that developers want to learn. Course information is stored in a simple local JSON file instead of a database.

This project helps beginners’ practice:

- REST API concepts
- HTTP methods
- JSON request and response bodies
- CRUD operations
- Flask routes
- File-based data storage

---

## Features

- Create new courses
- View all courses
- View one course by ID
- View course statistics by status
- Update an existing course
- Delete a course
- Automatically generate course IDs
- Automatically record course creation timestamps
- Store data in `courses.json`
- Automatically create `courses.json` if it does not exist
- Validate required fields
- Validate course status values
- Validate dates in `YYYY-MM-DD` format
- Return helpful error messages
- No database required
- No authentication required

---

## Technologies Used

- Python 3
- Flask
- JSON
- `curl` for testing API requests

---

## Project Structure

```text
codecrafthub/
├── app.py
├── courses.json
├── requirements.txt
├── README.md
└── venv/
```

### `app.py`

Contains the Flask application, API routes, validation logic, JSON file operations, and error handling.

### `courses.json`

Stores all courses as a JSON array.

Example:

```json
[
  {
    "id": 1,
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods and API design.",
    "target_date": "2026-12-31",
    "status": "Completed",
    "created_at": "2026-10-13T10:30:00+00:00"
  }
]
```

The application creates this file automatically if it does not exist.

### `requirements.txt`

Contains the Python packages needed by the application.

Example:

```text
Flask
```

### `README.md`

Contains the project documentation and instructions.

### `venv/`

Contains the Python virtual environment. This folder should normally not be committed to Git.

---

# Installation

## 1. Check that Python is installed

Open a terminal or command prompt and run:

```bash
python --version
```

On some systems, use:

```bash
python3 --version
```

You should have Python 3 installed.

If Python is not installed, download it from:

<https://www.python.org/downloads/>

Windows users should select **Add Python to PATH** during installation.

---

## 2. Create the project directory

```bash
mkdir codecrafthub
cd codecrafthub
```

---

## 3. Create a virtual environment

A virtual environment keeps this project's packages separate from other Python projects.

### macOS or Linux

```bash
python3 -m venv venv
```

### Windows

```bash
python -m venv venv
```

---

## 4. Activate the virtual environment

### macOS or Linux

```bash
source venv/bin/activate
```

### Windows Command Prompt

```cmd
venv\Scripts\activate
```

### Windows PowerShell

```powershell
venv\Scripts\Activate.ps1
```

After activation, your terminal may show `(venv)` at the beginning of the command prompt.

---

## 5. Install Flask

If `requirements.txt` exists, run:

```bash
pip install -r requirements.txt
```

Alternatively, install Flask directly:

```bash
pip install Flask
```

A basic `requirements.txt` file should contain:

```text
Flask
```

---

## 6. Add the project files

Place `app.py`, `requirements.txt`, and this `README.md` file in the project directory.

You do not have to create `courses.json` manually. The application creates it automatically.

If you create it yourself, its initial contents should be:

```json
[]
```

---

# Running the Application

Make sure the virtual environment is activated, then run:

```bash
python app.py
```

On some systems, use:

```bash
python3 app.py
```

The application should display something similar to:

```text
* Running on http://localhost:5000
```

The API is now available at:

```text
http://localhost:5000
```

Keep this terminal window open while testing the API.

To stop the application, press:

```text
Ctrl+C
```

---

## Debug Mode

The application normally runs with Flask debug mode enabled:

```python
app.run(debug=True)
```

Debug mode automatically reloads the application when code changes.

Debug mode is useful during development. It should be disabled in production:

```python
app.run(debug=False)
```

---

# REST API Concepts

A REST API uses:

- URLs to identify resources
- HTTP methods to describe actions
- JSON to send and receive data
- HTTP status codes to describe results

The main resource in CodeCraftHub is a course.

| HTTP Method | Meaning |
| --- | --- |
| `GET` | Retrieve data |
| `POST` | Create new data |
| `PUT` | Update existing data |
| `DELETE` | Delete data |

---

# Course Fields

Each course contains the following fields:

| Field | Description |
| --- | --- |
| `id` | Automatically generated numeric ID |
| `name` | Required course name |
| `description` | Required course description |
| `target_date` | Required date in `YYYY-MM-DD` format |
| `status` | Required status value |
| `created_at` | Automatically generated timestamp |

Valid status values are:

```text
Not Started
In Progress
Completed
```

Example course:

```json
{
  "id": 1,
  "name": "REST API Fundamentals",
  "description": "Learn HTTP methods, status codes, and API design.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-10-13T10:30:00+00:00"
}
```

The `id` and `created_at` fields are generated by the server.

---

# API Endpoints

Base URL:

```text
http://localhost:5000
```

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/courses` | Add a new course |
| `GET` | `/api/courses` | Get all courses |
| `GET` | `/api/courses/<id>` | Get one course |
| `PUT` | `/api/courses/<id>` | Update one course |
| `DELETE` | `/api/courses/<id>` | Delete one course |
| `GET` | `/api/courses/stats` | Get course statistics |

For example, the URL for course ID `1` is:

```text
http://localhost:5000/api/courses/1
```

---

## Create a Course

### Request

```text
POST /api/courses
```

### Example

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, and API design.",
    "target_date": "2026-12-31",
    "status": "Not Started"
  }'
```

### Successful response

Status:

```text
201 Created
```

Response:

```json
{
  "id": 1,
  "name": "REST API Fundamentals",
  "description": "Learn HTTP methods, status codes, and API design.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-10-13T10:30:00+00:00"
}
```

The actual `created_at` value will be different.

---

## Get All Courses

### Request

```text
GET /api/courses
```

### Example

```bash
curl http://localhost:5000/api/courses
```

### Successful response

Status:

```text
200 OK
```

Response:

```json
[
  {
    "id": 1,
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, and API design.",
    "target_date": "2026-12-31",
    "status": "Not Started",
    "created_at": "2026-10-13T10:30:00+00:00"
  }
]
```

If there are no courses, the response is:

```json
[]
```

---

## Get One Course

### Request

```text
GET /api/courses/<id>
```

### Example

```bash
curl http://localhost:5000/api/courses/1
```

### Successful response

Status:

```text
200 OK
```

Response:

```json
{
  "id": 1,
  "name": "REST API Fundamentals",
  "description": "Learn HTTP methods, status codes, and API design.",
  "target_date": "2026-12-31",
  "status": "Not Started",
  "created_at": "2026-10-13T10:30:00+00:00"
}
```

---

## Update a Course

The current application expects all required course fields in a `PUT` request.

### Request

```text
PUT /api/courses/<id>
```

### Example

```bash
curl -X PUT http://localhost:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, API design, and testing.",
    "target_date": "2026-12-31",
    "status": "In Progress"
  }'
```

### Successful response

Status:

```text
200 OK
```

Response:

```json
{
  "id": 1,
  "name": "REST API Fundamentals",
  "description": "Learn HTTP methods, status codes, API design, and testing.",
  "target_date": "2026-12-31",
  "status": "In Progress",
  "created_at": "2026-10-13T10:30:00+00:00"
}
```

The `id` and `created_at` values do not change during an update.

---

## Delete a Course

### Request

```text
DELETE /api/courses/<id>
```

### Example

```bash
curl -X DELETE http://localhost:5000/api/courses/1
```

### Successful response

Status:

```text
200 OK
```

Response:

```json
{
  "message": "Course deleted successfully",
  "course": {
    "id": 1,
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, and API design.",
    "target_date": "2026-12-31",
    "status": "In Progress",
    "created_at": "2026-10-13T10:30:00+00:00"
  }
}
```

---

## Course Statistics

`GET /api/courses/stats` returns a summary of the courses stored in `courses.json`.

The response includes:

- The total number of courses
- The number of courses for each status: Not Started, In Progress, and Completed

### Request

```text
GET /api/courses/stats
```

### Example

```bash
curl http://localhost:5000/api/courses/stats
```

### Successful response

Status:

```text
200 OK
```

Response:

```json
{
  "total": 2,
  "by_status": {
    "Not Started": 1,
    "In Progress": 1,
    "Completed": 0
  }
}
```

Each status is present even when its count is `0`.

A course with a status outside these three values is counted in `total` only.

If there are no courses, every count is `0`:

```json
{
  "total": 0,
  "by_status": {
    "Not Started": 0,
    "In Progress": 0,
    "Completed": 0
  }
}
```

---

# Error Responses

## Missing Required Fields

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Basics"
  }'
```

Response status:

```text
400 Bad Request
```

Response:

```json
{
  "error": "Missing required fields: description, target_date, status"
}
```

---

## Invalid Status

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Docker Basics",
    "description": "Learn the basics of Docker.",
    "target_date": "2026-12-15",
    "status": "Finished"
  }'
```

Response status:

```text
400 Bad Request
```

Response:

```json
{
  "error": "Invalid status. Status must be one of: Completed, In Progress, Not Started"
}
```

---

## Invalid Date

The date must use `YYYY-MM-DD` format.

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Docker Basics",
    "description": "Learn the basics of Docker.",
    "target_date": "15-12-2026",
    "status": "Not Started"
  }'
```

Response status:

```text
400 Bad Request
```

Response:

```json
{
  "error": "target_date must use YYYY-MM-DD format"
}
```

---

## Course Not Found

```bash
curl http://localhost:5000/api/courses/9999
```

Response status:

```text
404 Not Found
```

Response:

```json
{
  "error": "Course with ID 9999 not found"
}
```

The same type of response is returned when trying to update or delete a course that does not exist.

---

## Invalid JSON

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Python Basics",'
```

Response status:

```text
400 Bad Request
```

Response:

```json
{
  "error": "Request body must contain valid JSON"
}
```

---

# Testing Instructions

## Test with `curl`

Start the application:

```bash
python app.py
```

Open another terminal window and run:

```bash
curl http://localhost:5000/api/courses
```

To display response headers and status codes, use `-i`:

```bash
curl -i http://localhost:5000/api/courses
```

---

## Complete CRUD Test Sequence

### 1. Get all courses

```bash
curl http://localhost:5000/api/courses
```

### 2. Create a course

```bash
curl -X POST http://localhost:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, and API design.",
    "target_date": "2026-12-31",
    "status": "Not Started"
  }'
```

### 3. Get course ID 1

```bash
curl http://localhost:5000/api/courses/1
```

### 4. Update course ID 1

```bash
curl -X PUT http://localhost:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "REST API Fundamentals",
    "description": "Learn HTTP methods, status codes, API design, and testing.",
    "target_date": "2026-12-31",
    "status": "In Progress"
  }'
```

### 5. Get all courses again

```bash
curl http://localhost:5000/api/courses
```

### 6. Get course statistics

```bash
curl http://localhost:5000/api/courses/stats
```

### 7. Delete course ID 1

```bash
curl -X DELETE http://localhost:5000/api/courses/1
```

### 8. Confirm deletion

```bash
curl http://localhost:5000/api/courses/1
```

The command above should return a `404 Not Found` response.

### 9. Get course statistics again

```bash
curl http://localhost:5000/api/courses/stats
```

The deleted course is no longer included in the totals.

---

## Testing with Postman or Insomnia

You can also use an API client such as:

- Postman
- Insomnia
- Thunder Client for Visual Studio Code

For `POST` and `PUT` requests:

1. Create a new request.
2. Select `POST` or `PUT`.
3. Enter the request URL.
4. Add this header:

   ```text
   Content-Type: application/json
   ```

5. Select a raw JSON request body.
6. Enter a course payload.
7. Send the request.

Example request body:

```json
{
  "name": "Flask Web Development",
  "description": "Build web applications and REST APIs with Flask.",
  "target_date": "2027-01-15",
  "status": "In Progress"
}
```

---

# How JSON File Storage Works

The application uses Python's built-in `json` module.

When retrieving courses:

1. The application opens `courses.json`.
2. It reads the JSON contents.
3. It converts the JSON into Python objects.
4. It returns the courses in the API response.

When adding, updating, or deleting courses:

1. The application reads the existing courses.
2. It changes the Python list.
3. It writes the updated list back to `courses.json`.

This approach is suitable for a small learning project.

A JSON file is not ideal for a large application because:

- The entire file is read and rewritten for changes.
- Simultaneous writes may cause conflicts.
- There are no database queries or indexes.
- There is no built-in user access control.
- The file should be backed up regularly.

---

# Troubleshooting

## Flask is not installed

Error:

```text
ModuleNotFoundError: No module named 'flask'
```

Solution:

```bash
pip install Flask
```

Or:

```bash
pip install -r requirements.txt
```

---

## Python command is not recognized

Try:

```bash
python3 app.py
```

You can check the installed Python version with:

```bash
python --version
```

or:

```bash
python3 --version
```

On Windows, reinstall Python and select:

```text
Add Python to PATH
```

---

## The virtual environment will not activate

On Windows Command Prompt, use:

```cmd
venv\Scripts\activate
```

On macOS or Linux, use:

```bash
source venv/bin/activate
```

---

## Address already in use

This means another application is already using port `5000`.

Stop the other process with:

```text
Ctrl+C
```

Alternatively, change the port in `app.py`:

```python
app.run(debug=True, port=5001)
```

Then use:

```text
http://localhost:5001
```

---

## Connection refused

Make sure the Flask application is running:

```bash
python app.py
```

Also verify that the URL is correct:

```text
http://localhost:5000
```

---

## `courses.json` contains invalid JSON

The file must contain valid JSON.

An empty course file should contain:

```json
[]
```

To reset all course data, stop the application and replace the contents of `courses.json` with:

```json
[]
```

Warning: this deletes all saved courses.

---

## `courses.json` is not created

Check that:

- You are running the correct `app.py` file.
- The project folder is writable.
- The application starts without a permission error.
- You have permission to create files in the project folder.

The application creates the file automatically when it starts.

---

## `curl` commands do not work on Windows

The multi-line commands in this README use Unix-style line continuation with `\`.

On Windows Command Prompt, use a single line:

```cmd
curl -X POST http://localhost:5000/api/courses -H "Content-Type: application/json" -d "{\"name\":\"Python Basics\",\"description\":\"Learn Python programming.\",\"target_date\":\"2026-12-01\",\"status\":\"Not Started\"}"
```

---

## Course IDs are different from expected

Course IDs are generated automatically.

The first course receives ID `1`. New courses receive the next highest ID.

Deleting a course does not automatically reuse its ID.

For example, if the current IDs are:

```text
1, 2, 3
```

the next course receives:

```text
4
```

---

# Future Improvements

Possible future improvements include:

- Add a web-based user interface
- Add course searching
- Add filtering by status
- Add sorting by target date
- Add pagination
- Add automated tests with `pytest`
- Replace the JSON file with SQLite
- Add authentication
- Add multiple users
- Add course categories
- Add progress percentages
- Add due-date reminders
- Add Swagger or OpenAPI documentation

---

# License

This project is intended for learning and educational purposes.