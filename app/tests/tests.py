import pytest
from app import app  # Ensure your app is imported correctly
from extensions import db
from models import Book

# Test setup with the database pointing to your existing books.db
@pytest.fixture
def test_app():
    """Set up the test Flask app using the existing books.db in the instance folder."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///instance/books.db"  # Ensure the correct path to books.db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        yield app  # Run the test
        db.session.remove()  # Clean up session after the test

# Provide the Flask test client for sending requests
@pytest.fixture
def client(test_app):
    """Provide the Flask test client."""
    return test_app.test_client()

# Test for /search
def test_get_books_by_phrase(client):
    # Ensure there's at least one book with the title containing "Moby"
    response = client.get('/books/search?phrase=Moby')  # Search for books containing "Moby"
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0  # Ensure that at least one book is found
    assert any(book['title'] == "Moby Dick" for book in data)  # Ensure the book "Moby Dick" is returned

# Test for /length
def test_get_books_by_author_length(client):
    # Ensure that we have at least one book where the author's name is longer than 5 characters
    response = client.get('/books/length?min_length=5')  # Use a length of 5 as an example
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0  # Ensure that books are returned
    assert all(len(book['author']) >= 5 for book in data)  # Ensure authors' names are >= 5 characters



# Test for /delete_by_author (delete a single author)
def test_delete_books_by_author(client):
    # Delete books by a specific author (example: "F. Scott Fitzgerald")
    response = client.delete('/books/delete_by_author?author=F. Scott Fitzgerald')
    assert response.status_code == 200
    assert response.get_json()['message'] == "1 books deleted"  # Assuming only one book by that author

    # Verify that the book has been deleted
    with app.app_context():
        book = Book.query.filter_by(author="F. Scott Fitzgerald").first()
        assert book is None  # Ensure the book no longer exists

# Test for /stats
def test_get_book_statistics(client):
    # Test for statistics (average title length, most common year, books per year)
    response = client.get('/books/stats')
    assert response.status_code == 200
    data = response.get_json()

    # Ensure that the statistics data contains expected values
    assert data['average_title_length'] > 0  # Ensure average title length is calculated
    assert data['most_common_year'] is not None  # Ensure the most common year is present
    assert len(data['books_per_year']) > 0  # Ensure books per year data is present
