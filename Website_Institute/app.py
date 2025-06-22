import re
from flask import Flask, request, jsonify, render_template, session ,redirect, url_for , flash
import openai
import os
import dotenv
import json
import difflib
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
# import requests # Uncomment this if you decide to use Hugging Face in the future


app = Flask(__name__)

# Load predefined static responses
with open("responses.json", "r") as f:
    static_responses = json.load(f)

# Set your OpenAI API key (can be removed if not used anywhere else)
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Hugging Face API Configuration (currently commented out) ---
# HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY")
# HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
# HEADERS = {
#     "Authorization": f"Bearer {HUGGING_FACE_API_KEY}"
# }

#setup database connection
#initialize mysql connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'anas'
app.config['MYSQL_PASSWORD'] = 'neotech@223'
app.config['MYSQL_DB'] = 'neotech_db'

# setup session time
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=20)

# Initialize MySQL connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    # --- Currently using OpenAI ---
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4", # Or "gpt-3.5-turbo" if preferred
            messages=[
                {"role": "system", "content": "You are a helpful assistant for NeoTech Institute. Provide concise answers."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})

    except Exception as e:
        print(f"⚠️ OpenAI API failed: {e}")

        # Fallback to difflib if OpenAI API fails
        possible_keys = list(static_responses.keys())
        best_match = difflib.get_close_matches(user_message, possible_keys, n=1, cutoff=0.5)

        if best_match:
            reply = static_responses[best_match[0]]
        else:
            reply = static_responses.get("default", "Sorry, I didn't understand that.")

        return jsonify({"response": reply})


# Route for handling user registration (General Inquiry Form)
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    contact = data.get("contact", "").strip() # Ensure contact is stripped of whitespace

    if not name or not contact:
        return jsonify({"success": False, "message" : "Full name and Email/Phone number are required."}), 400

    # --- Validation logic ---
    is_email = re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", contact)
    is_phone = re.match(r"^\+?[0-9\s\-\(\)]{7,20}$", contact) # Corrected phone number regex

    if not is_email and not is_phone:
        return jsonify({"success": False, "message": "Please enter a valid email or phone number."}), 400
    # --- End validation logic ---

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message" : "Database connection failed."}), 500

    cursor = conn.cursor()

    try:
        # Check if the user already exists (using email as the unique identifier in students table)
        # This still checks if they are already an *enrolled student* by their contact email
        cursor.execute("SELECT student_pk_id FROM students WHERE email = %s", (contact,))
        existing_user = cursor.fetchone()
        if existing_user:
            # If the contact is an email and already exists as a student
            return jsonify({"success": False , "message": "A student account already exists with this email. Please use the Login page."}), 409
        
        # If it's a general inquiry and not an existing student, proceed
        print(f"Registering user for general enquiry: Name={name},Contact={contact}")
        
        # As discussed, this route DOES NOT insert into the 'students' table.
        # If you later decide to store these general inquiries, you'll add an INSERT statement
        # into a new 'inquiries' table here.

        return jsonify({"success": True, "message": "Thank you for your interest! We'll contact you soon."}) # Corrected comma here
    except mysql.connector.Error as err:
        print(f"❌ Database error during general registration: {err}")
        return jsonify({"success": False, "message": "Failed to process registration due to a server error."}), 500
    finally:
        cursor.close()
        conn.close()

# --- New Route for Student Registration (with password and Program Selection) ---
@app.route("/student_signup", methods=["GET", "POST"])
def student_signup():
    conn = get_db_connection()
    if conn is None:
        flash("Database connection error.", "danger")
        return render_template("student_signup.html", programs=[]) # Pass empty list if no connection

    cursor = conn.cursor(dictionary=True) # Return rows as dictionaries
    programs = []
    try:
        cursor.execute("SELECT program_id, program_name FROM programs ORDER BY program_name")
        programs = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"❌ Database error fetching programs: {err}")
        flash("Could not load academic programs. Please try again later.", "danger")
    finally:
        cursor.close()
        # Close connection for GET request path, re-open for POST if needed
        # Or keep open if POST is handled in same block, but better to close/reopen
        # if logic branches significantly. Here, we'll explicitly close.
        conn.close()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        program_id = request.form.get("program_id") # Get selected program ID

        if not email or not password or not full_name or not program_id:
            flash("All fields, including program selection, are required for student registration.", "danger")
            # If validation fails, re-render the form with programs list
            return render_template("student_signup.html", programs=programs)

        # Re-establish connection for POST request
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error.", "danger")
            return render_template("student_signup.html", programs=programs)

        cursor = conn.cursor()
        try:
            # Check if email already exists
            cursor.execute("SELECT student_pk_id FROM students WHERE email = %s", (email,))
            existing_student = cursor.fetchone()
            if existing_student:
                flash("A student with this email already exists.", "warning")
                return render_template("student_signup.html", programs=programs)

            # Hash the password before storing
            hashed_password = generate_password_hash(password)

            # Insert new student into the database including program_id
            sql = """
            INSERT INTO students (email, password_hash, full_name, program_id, enrollment_date, student_status)
            VALUES (%s, %s, %s, %s, CURRENT_DATE(), 'Active')
            """
            cursor.execute(sql, (email, hashed_password, full_name, program_id))
            conn.commit()
            flash("Student registration successful! You can now log in.", "success")
            return redirect(url_for("login")) # Redirect to login page

        except mysql.connector.Error as err:
            print(f"❌ Database error during student signup: {err}")
            flash("An error occurred during registration. Please try again.", "danger")
        finally:
            if conn and conn.is_connected(): # Check if connection is still open before closing
                cursor.close()
                conn.close()
    
    # For GET request, or if POST fails before database interaction (e.g., validation)
    # The 'programs' variable will already be populated from the initial GET-path database call.
    return render_template("student_signup.html", programs=programs)


# --- New Route for Student Login ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        if conn is None:
            flash("Database connection error.", "danger")
            return render_template("login.html")

        cursor = conn.cursor(dictionary=True) # Return rows as dictionaries
        try:
            # Use student_pk_id for selection
            cursor.execute("SELECT student_pk_id, email, password_hash, full_name FROM students WHERE email = %s", (email,))
            student = cursor.fetchone()

            if student and check_password_hash(student['password_hash'], password):
                # Password is correct, set session variables
                session['logged_in'] = True
                session['student_id'] = student['student_pk_id']
                session['student_email'] = student['email']
                session['student_name'] = student['full_name']
                flash(f"Welcome, {student['full_name']}!", "success")
                return redirect(url_for("student_dashboard"))

            else:
                flash("Invalid email or password.", "danger")
        except mysql.connector.Error as err:
            print(f"❌ Database error during login: {err}")
            flash("An error occurred during login. Please try again.", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("login.html")


# --- New Route for Student Dashboard (Protected) ---
@app.route("/student_dashboard")
def student_dashboard():
    if 'logged_in' not in session or not session['logged_in']:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    student_name = session.get('student_name', 'Student')
    student_email = session.get('student_email')
    student_id = session.get('student_id')

    # Fetch more student details including program name
    conn = get_db_connection()
    student_info = {}
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
            SELECT s.full_name, s.email, p.program_name, s.current_academic_year, s.student_status
            FROM students s
            LEFT JOIN programs p ON s.program_id = p.program_id
            WHERE s.student_pk_id = %s
            """
            cursor.execute(sql, (student_id,))
            student_info = cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"❌ Database error fetching student dashboard info: {err}")
            flash("Could not load full student details.", "danger")
        finally:
            cursor.close()
            conn.close()

    # If student_info is not populated due to error or no data, use session defaults
    if not student_info:
        student_info = {
            'full_name': student_name,
            'email': student_email,
            'program_name': 'N/A',
            'current_academic_year': 'N/A',
            'student_status': 'N/A'
        }

    return render_template("student_dashboard.html", student_info=student_info)


# --- New Route for Logout ---
@app.route("/logout")
def logout():
    session.clear() # Clear all session variables
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)