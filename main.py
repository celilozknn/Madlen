from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

app = Flask(__name__)


def validate_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False
    
@app.route('/scrape', methods=['POST'])
def scrape_notes():
    data = request.json
    url = data.get('url')
    course_title = data.get('course_title')
    grade_level = data.get('grade_level')

    # Validate input
    if not url or not course_title or not grade_level:
        return jsonify({'error': 'Missing required fields'}), 400

    # URL Validation: Verify that the provided URL is accessible
    if not validate_url(url):
        return jsonify({'error': 'Invalid URL or unable to access the page'}), 400

    # Scrape content from the URL
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        soup = BeautifulSoup(response.text, 'html.parser')

        # Content Extraction
        extracted_content = extract_content(soup)

        # Save data to the database
        note_id = save_to_db(url, course_title, grade_level, extracted_content)

        return jsonify({
            'message': 'Content scraped and stored successfully',
            'note_id': note_id
        }), 201

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to retrieve URL: {str(e)}'}), 500

def extract_content(soup):
    structured_content = {}
    
    # Extract headers and their corresponding content
    for header in soup.find_all(['h1', 'h2', 'h3']):
        section_title = header.text.strip()
        section_content = []

        # Get the next siblings until the next header
        for sibling in header.find_next_siblings():
            if sibling.name and sibling.name.startswith('h'):  # Stop at the next header
                break
            if sibling.name in ['p', 'ul', 'ol', 'table']:  # Include paragraphs, lists, and tables
                section_content.append(str(sibling))

        # Store the structured content
        structured_content[section_title] = section_content

    # Convert structured content to a string format (or keep it as dict if preferred)
    content = '\n\n'.join([f"{title}\n{''.join(content)}" for title, content in structured_content.items()])
    
    return content

# Database setup
def init_db():
    conn = sqlite3.connect("lecture_notes.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            course_title TEXT NOT NULL,
            grade_level TEXT NOT NULL,
            content TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def manual_add_data_to_db(ind):
    conn = sqlite3.connect("lecture_notes.db")
    c = conn.cursor()

    c.execute("""INSERT INTO notes VALUES(?,?,?,?,?,?)""", 
              (ind, "https://madlen.io", "Functions", "9", "Content", "Date"))
    conn.commit()
    conn.close()

def save_to_db(url, course_title, grade_level, content):
    try:
        conn = sqlite3.connect("lecture_notes.db")
        c = conn.cursor()

        # Save obtained data, id will be handled by the db since it's autoincremented
        current_time = datetime.now().isoformat()
        c.execute('''
            INSERT INTO notes (url, course_title, grade_level, content, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, course_title, grade_level, content, current_time))
        conn.commit()

        note_id = c.lastrowid  # Get the ID of the last inserted row, to check
        return note_id
    
    except sqlite3.Error as e: # Some error occured, inform the programmer
        print(f"Database error: {e}")
        return None
    
    finally:
        conn.close()

# Function to get all db content, prints its content line by line (no return line)
def get_all_db():
    conn = sqlite3.connect("lecture_notes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes") 
    all_content = c.fetchall()  # Fetch all results
    conn.close()

    # Print results for debugging
    for content in all_content:
        print(content)

def remove_db():
    conn = sqlite3.connect("lecture_notes.db")
    c = conn.cursor()
    c.execute("""DROP TABLE notes""")
    conn.close()


url = "https://madlen.io"
title = "functions"
grade = "9"
content = "content"
print(f"Succesfully saved the data with index: {save_to_db(url, title, grade, content)}")
# manual_add_data_to_db(7)

if __name__ == '__main__':
    init_db()
    # remove_db()
    get_all_db()
    #app.run(debug=True)
