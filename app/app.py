from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from extensions import db
from books import books_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)  # Ensure Bootstrap is applied to the app
db.init_app(app)

app.register_blueprint(books_bp, url_prefix='/books')

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
