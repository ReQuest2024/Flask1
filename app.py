from flask import Flask, abort, jsonify, request
import random
from pathlib import Path
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Для вывода содержимого SQL запросов
# app.config["SQLALCHEMY_ECHO"] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name):
       self.name = name

    def __repr__(self):
        return f'Author({self.name})'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


class QuoteModel(db.Model):
    __tablename__ = "quote"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id), nullable=False)
    text = db.Column(db.String(255), unique=False, nullable=False)

    def __init__(self, author, text):
       self.author_id = author.id
       self.text  = text

    def __repr__(self):
        return f'Quote({self.text})'

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author_id,
            "text": self.text
        }

# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


## Authors
# GET на url: /authors              # получить список авторов
@app.get("/authors")
def get_all_authors():
    authors_lst = db.session.query(AuthorModel)   
    authors_lst_dct = []
    for author in authors_lst:
        authors_lst_dct.append(author.to_dict())
    return jsonify(authors_lst_dct), 200


# GET на url: /authors/<int:author_id>     # получить автора с id = <int:author_id>
@app.get("/authors/<int:author_id>")
def get_author_by_id(author_id):
    author = db.session.get(AuthorModel, author_id)   
    if author:
        return jsonify(author.to_dict()), 200
    abort(404, f"Author with author_id = {author_id} not found")


# POST на url: /authors             # создать нового автора
@app.post("/authors")
def create_author():
    author_data = request.json
    authors_name = db.session.query(AuthorModel).filter_by(name = author_data.get("name", "noname"))
    if len(authors_name.all()):
        abort(500, f"Author with name = '{author_data.get('name', 'noname')}' already exists")
    author = AuthorModel(author_data.get("name", "noname")) 
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201


# PUT на url: /authors/<int:id>     # обновить автора с id = <int:id>
@app.put("/authors/<int:author_id>")
def edit_author_by_id(author_id):
    new_data = request.json
    author = db.session.get(AuthorModel, author_id)   
    if not author:
        abort(404, f"Author with author_id = {author_id} not found")
    authors_name = db.session.query(AuthorModel).filter_by(name = new_data.get("name", "noname"))
    if len(authors_name.all()):
        abort(500, f"Author with name = '{new_data.get('name', 'noname')}' already exists")
    for key, value in new_data.items():
        setattr(author, key, value)
    try:
        db.session.commit()
        return jsonify(author.to_dict()), 200
    except:
        abort(500)


# DELETE на url: /authors/<int:id>  # удалить автора с id = <int:id>
@app.delete("/authors/<int:author_id>")
def delete_author_by_id(author_id):
    quote = db.session.get(AuthorModel, author_id)
    if quote:
        db.session.delete(quote)
        db.session.commit()
        return {"message": f"Author with author_id = {author_id} deleted."}, 200
    abort(404, f"Author with author_id = {author_id} not found")



## Quotes
# GET на url: /quotes/              # все цитаты всех авторов
@app.route("/quotes")
def get_all_quotes():
    quotes_lst = db.session.query(QuoteModel)   
    quotes_lst_dct = []
    for quote in quotes_lst:
        quotes_lst_dct.append(quote.to_dict())
    return jsonify(quotes_lst_dct), 200


# GET на url: /quotes/<int:quote_id>      # получить цитату с quote_id = <int:quote_id>
@app.get("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = db.session.get(QuoteModel, quote_id)   
    if not quote is None:
        return jsonify(quote.to_dict()), 200
    abort(404, f"Quote with quote_id = {quote_id} not found")


# GET на url: /authors/<int:id>/quotes      # получить все цитаты автора с quote_id = <int:quote_id>
@app.get("/authors/<int:author_id>/quotes")
def get_quote_by_author(author_id):
    quotes_lst = db.session.query(QuoteModel).filter_by(author_id = author_id)   
    quotes_lst_dct = []
    for quote in quotes_lst:
        quotes_lst_dct.append(quote.to_dict())
    return jsonify(quotes_lst_dct), 200


# POST на url: /authors/<int:id>/quotes      # создать цитату для автора с quote_id = <int:quote_id>
@app.post("/authors/<int:author_id>/quotes")
def create_quote_to_author(author_id):
    author = db.session.get(AuthorModel, author_id)   
    if not author:
        abort(404, f"Author with author_id = {author_id} not found")
    data = request.json
    new_quote = QuoteModel(author, data.get("text", "blank")) 
    db.session.add(new_quote)
    db.session.commit()
    return new_quote.to_dict(), 201


# PUT на url: /quotes/<int:quote_id>     # обновить цитату с quote_id = <int:quote_id>
@app.put("/quotes/<int:quote_id>")
def edit_quote_by_id(quote_id):
    new_data = request.json
    quote = db.session.get(QuoteModel, quote_id) 
    if not quote:
        abort(404, f"Quthor with quote_id = {quote_id} not found")
    for key, value in new_data.items():
        setattr(quote, key, value)
    try:
        db.session.commit()
        return jsonify(quote.to_dict()), 200
    except:
        abort(500)


# DELETE на url: /quotes/<int:quote_id>  # удалить цитату с quote_id = <int:quote_id>
@app.delete("/quotes/<int:quote_id>")
def delete_quote_by_id(quote_id):
    quote = db.session.get(QuoteModel, quote_id)
    if quote:
        db.session.delete(quote)
        db.session.commit()
        return {"message": f"Quote with quote_id = {quote_id} deleted."}, 200
    abort(404, f"Quote with quote_id = {quote_id} not found")





if __name__ == "__main__":
   app.run(debug=True)