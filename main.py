from flask import Flask as f

app = f(__name__)
 
@app.route("/") # web adress entered such as madlen.io
def index():
    return "Hello Madlen User!"



app.run(host= "0.0.0.0", port= "80")


"""
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_content():
    data = request.json
    url = data.get('url')
    course_title = data.get('course_title')
    grade_level = data.get('grade_level')
    # Placeholder for scraping and storing logic
    return jsonify({"message": "Scraping started for URL", "url": url})

if __name__ == '__main__':
    app.run(debug=True)
"""