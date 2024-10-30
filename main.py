from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Scraping functions:

def validate_url(url):
    try:
        # Header is usually required since many websites require a user-agent to identify 
        # whether it will be allowed or not
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
        }
        response = requests.get(url, headers= headers)
        return response.status_code == 200
    except requests.RequestException as e: # Base exception, will handle all cases such as time-out, connection or http
        print(f"An error occurred: {e}")   # Inform programmer about the exception cause
        return False

@app.route('/scrape', methods=['POST'])
def scrape_notes():

    # parse for example "{"url": "http://madlen.io", "course_title": "Mathematics", "grade_level": "10th"})"
    data = request.json 
    url = data.get('url') # If not found becomes none, 
    course_title = data.get('course_title')
    grade_level = data.get('grade_level')

    # Validate input
    if not url or not course_title or not grade_level:  # We need all of these inputs
        return jsonify({'error': 'Missing required fields'}), 400 # Bad request

    # URL Validation: Verify that the provided URL is accessible
    if not validate_url(url):
        return jsonify({'error': 'Invalid URL or unable to access the page'}), 400 # Bad request

    # Set up headers for scraping
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }

    # Scrape content from the URL
    try:
        response = requests.get(url, headers = headers)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses, although we checked it might be changed
        soup = BeautifulSoup(response.text, 'html.parser')

        # Content Extraction
        extracted_content = extract_content(soup)

        # Save data to the database
        note_id = save_to_db(url, course_title, grade_level, extracted_content)

        return jsonify({
            'message': 'Content scraped and stored successfully',
            'note_id': note_id
        }), 201 # Request handled and new resource has been created

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to retrieve URL: {str(e)}'}), 500 # Internal server error

@app.route('/notes', methods=['GET'])
def get_notes():

    # Retrieve the ID from the request arguments (Additional)
    note_id = request.args.get('id')
    # Optional Parameters
    url = request.args.get('url')
    course_title = request.args.get('course_title')
    grade_level = request.args.get('grade_level')

    # Construct the query
    query = "SELECT * FROM notes WHERE 1=1"
    params = []

    if note_id:  # Check if ID is provided
        query += " AND id = ?"
        params.append(note_id)
    if url:
        query += " AND url = ?"
        params.append(url)
    if course_title:
        query += " AND course_title = ?"
        params.append(course_title)
    if grade_level:
        query += " AND grade_level = ?"
        params.append(grade_level)

    conn = sqlite3.connect("lecture_notes.db")
    c = conn.cursor()
    c.execute(query, params)
    notes = c.fetchall()
    conn.close()

    if not notes:
        return jsonify({'message': 'No notes found for the specified criteria.'}), 404

    # Format the response
    result = []
    for note in notes:
        result.append({
            'id': note[0],
            'url': note[1],
            'course_title': note[2],
            'grade_level': note[3],
            'content': note[4],
            'date': note[5],
        })

    return jsonify(result), 200

def extract_content(soup):
    structured_content = {}
    
    # Extract headers and their corresponding content
    for header in soup.find_all(['h1', 'h2', 'h3']):
        section_title = header.text.strip()  # Get the header text
        section_content = []

        # Get the next siblings until the next header
        for sibling in header.find_next_siblings():
            if sibling.name and sibling.name.startswith('h'):  # Stop at the next header
                break
            if sibling.name in ['p', 'ul', 'ol', 'table']:  # Include paragraphs, lists, and tables
                # Extract text from the sibling instead of the whole HTML
                section_content.append(sibling.get_text(strip=True))

        # Store the structured content
        structured_content[section_title] = section_content

    # Convert structured content to a string format
    # We do this since as far as I see storing a text for columns of db is a better practice
    content = '\n\n'.join([f"{title}\n{''.join(content)}" for title, content in structured_content.items()])
    return content

"""
# Code to check whether extract content works fine
with open("ext_cont.html", "r") as f:
    html_content = f.read()
    soup = BeautifulSoup(html_content, "html.parser")
    ext_con = extract_content(soup)
    print(ext_con)
"""

# Database functions:

# Database setup
def create_db():
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

# Manually add a data with index
def manual_add_data_to_db(ind):
    conn = sqlite3.connect("lecture_notes.db")
    c = conn.cursor()

    c.execute("""INSERT INTO notes VALUES(?,?,?,?,?,?)""", 
              (ind, "https://madlen.io", "Functions", "9", "Content", "Date"))
    conn.commit()
    conn.close()

# Main save function to save scraped data into db
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

# Get all db content, prints its content line by line (no return line)
def get_all_db():
    conn = sqlite3.connect("lecture_notes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM notes") 
    all_content = c.fetchall()  # Fetch all results
    conn.close()

    # Print results for debugging
    for content in all_content:
        print(content)

# Remove all db content and also table
def remove_db():
    conn = sqlite3.connect("lecture_notes.db")
    c = conn.cursor()
    c.execute("""DROP TABLE notes""")
    conn.close()

"""
# A few dummy code lines to check whether db works as intended:
# url = "https://madlen.io"
# title = "functions"
# grade = "9"
# content = "content"
# print(f"Succesfully saved the data with index: {save_to_db(url, title, grade, content)}")
# manual_add_data_to_db(7)
"""

if __name__ == '__main__':
    pass
    # create_db()
    # remove_db()
    # get_all_db()
    app.run(debug=True)

# References:
# https://www.youtube.com/watch?v=zsYIw6RXjfM  # Flask get post methods
# https://www.youtube.com/watch?v=XVv6mJpFOb0  # Web scraping
# https://www.youtube.com/watch?v=T1xAqWNdfoY  # Database operations
# https://www.youtube.com/watch?v=KgWhlrpL4Ao  # Sibling operation

# Check whether syntax is correct, and get some help to how to design some parts
# I also used gpt to have better understanding of some concepts, some parts of the scraping for example
# https://chatgpt.com

# https://flask.palletsprojects.com/en/stable/ # Flask docs which I didn't use extensively
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/ # Use to get better understanging of bs4, not used extensively