from flask import Blueprint, jsonify, request, render_template, url_for, redirect
from extensions import db
from .models import Book
from sqlalchemy.sql import func


# Initialize the Blueprint
books_bp = Blueprint('books', __name__, template_folder='../templates')

# ------------------- Existing Book Routes -------------------
#GUI Query1
@books_bp.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        year = request.form.get("year")
        new_book = Book(title=title, author=author, year=int(year))
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("books.view_books"))
    return render_template("add_book.html")
#GUI Query2
@books_bp.route("/")
def view_books():
    books_list = Book.query.all()
    return render_template("view_all_books.html", books=books_list)
#GUI Query3
@books_bp.route("/books/filter", methods=["GET"])
def filter_books_by_genre():
    genre = request.args.get("genre")
    books_list = Book.query.filter_by(genre=genre).all()
    return render_template("filter_books.html", books=books_list, filter_genre=genre)
#GUI Query4
@books_bp.route("/books/sort", methods=["GET"])
def sort_books_by_title():
    order = request.args.get("order", "asc")
    if order == "desc":
        books_list = Book.query.order_by(Book.title.desc()).all()
    else:
        books_list = Book.query.order_by(Book.title.asc()).all()
        return render_template("sort_books.html", books=books_list, order=order)
#GUI Query5
@books_bp.route("/books/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == "POST":
        book.title = request.form.get("title", book.title)
        book.author = request.form.get("author", book.author)
        book.genre = request.form.get("genre", book.genre)
        book.publish_date = request.form.get("publish_date", book.publish_date)
        db.session.commit()
        return render_template("view_all_books.html", books=Book.query.all(), message="Book␣updated␣successfully!")
    return render_template("edit_book.html", book=book)
#GUI Query6
@books_bp.route("/books/delete/<int:id>", methods=["POST"])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return render_template("view_all_books.html", books=Book.query.all(), message="Book␣deleted␣successfully!")

#GUI Query7
@books_bp.route("/books/count-by-genre", methods=["GET"])
def count_books_by_genre():
    counts = db.session.query(Book.genre, db.func.count(Book.genre)).group_by(Book.genre).all()
    return render_template("count_books.html", counts=counts)
# ------------------- New Feedback Comment Routes -------------------

#API Query1
@books_bp.route("/search", methods=["GET"])
def get_books_by_phrase():
    """Retrieve books with a specific phrase in the title."""
    phrase = request.args.get('phrase', '').strip()
    if not phrase:
        return jsonify({"error": "Phrase is required"}), 400
    books = Book.query.filter(Book.title.ilike(f"%{phrase}%")).all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "year": book.year} for book in books]), 200

#API Query2
@books_bp.route("/length", methods=["GET"])
def get_books_by_author_length():
    """Retrieve books where the author's name meets a minimum length."""
    min_length = request.args.get('min_length', type=int)
    if min_length is None:
        return jsonify({"error": "min_length is required"}), 400
    books = Book.query.filter(func.length(Book.author) >= min_length).all()
    return jsonify([{"id": book.id, "title": book.title, "author": book.author, "year": book.year} for book in books]), 200

#API Query3
@books_bp.route("/update", methods=["PUT", "PATCH"])
def update_multiple_books():
    """Batch update book information."""
    data = request.get_json()
    ids = data.get('ids', [])
    new_year = data.get('year')

    if not ids or not new_year:
        return jsonify({"error": "ids and year are required"}), 400

    books = Book.query.filter(Book.id.in_(ids)).all()
    for book in books:
        book.year = new_year
    db.session.commit()

    return jsonify({"message": f"{len(books)} books updated"}), 200

#API Query4 TBC
@books_bp.route("/delete_by_author", methods=["DELETE"])
def delete_books_by_author():
    """Delete all books by a specific author."""
    author_name = request.args.get('author')
    if not author_name:
        return jsonify({"error": "author is required"}), 400

    deleted_count = Book.query.filter_by(author=author_name).delete()
    db.session.commit()

    return jsonify({"message": f"{deleted_count} books deleted"}), 200

#API Query5
@books_bp.route("/stats", methods=["GET"])
def get_book_statistics():
    """Retrieve statistics about books."""
    avg_title_length = db.session.query(func.avg(func.length(Book.title))).scalar()
    most_common_year = db.session.query(Book.year, func.count(Book.year))\
                                  .group_by(Book.year)\
                                  .order_by(func.count(Book.year).desc()).first()
    books_per_year = db.session.query(Book.year, func.count(Book.id))\
                               .group_by(Book.year).all()

    stats = {
        "average_title_length": avg_title_length or 0,
        "most_common_year": most_common_year[0] if most_common_year else None,
        "books_per_year": {year: count for year, count in books_per_year}
    }
    return jsonify(stats), 200

#API Query6
