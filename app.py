import os
import psycopg2
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "job_scraper")
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")

app = Flask(__name__)

def connect_db():
    """Connect to PostgreSQL."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )

@app.route("/")
def home():
    """Display job listings with search functionality."""
    keyword = request.args.get("keyword", "").strip()
    location = request.args.get("location", "").strip()

    conn = connect_db()
    cursor = conn.cursor()

    query = "SELECT title, company, location, link FROM jobs WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title ILIKE %s OR company ILIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if location:
        query += " AND location ILIKE %s"
        params.append(f"%{location}%")

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("index.html", jobs=jobs, keyword=keyword, location=location)

if __name__ == "__main__":
    app.run(debug=True)
