# Flask Web Scraping and Storage API

This application is a Flask-based API designed to scrape web content and store it in a SQLite database. It validates URLs, scrapes specific sections of a webpage, and saves structured content as text in the database. The API also supports querying for saved notes based on various criteria.

## Features

- **URL Validation**: Ensures that the provided URL is reachable and valid.
- **Content Extraction**: Scrapes headers and relevant sections, organizing them into a structured format.
- **Database Storage**: Saves scraped content along with metadata such as course title, grade level, and scrape date.
- **Query Support**: Retrieves saved notes based on optional parameters like URL, course title, and grade level.

## Requirements

- Python 3.x
- Flask
- Requests
- BeautifulSoup4 (bs4)
- SQLite3 (built-in with Python)






