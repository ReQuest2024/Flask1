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


@app.post("/authors")
def create_author():
    author_data = request.json
    author = AuthorModel(author_data.get("name", "noname")) 
    db.session.add(author)
    db.session.commit()
    return jsonify(author.to_dict()), 201


@app.post("/authors/<int:author_id>/quotes")
def create_quote_to_author(author_id):
    author = AuthorModel.query.get(author_id)
    data = request.json
    new_quote = QuoteModel(author, data.get("text", "blank")) 
    db.session.add(new_quote)
    db.session.commit()
    return new_quote.to_dict(), 201


# GET на url: /quotes/
@app.route("/quotes")
def get_quotes():
    quotes_lst = db.session.query(QuoteModel)   
    quotes_lst_dct = []
    for quote in quotes_lst:
        quotes_lst_dct.append(quote.to_dict())
    return jsonify(quotes_lst_dct), 200


# GET на url: /quotes/<int:id>
@app.get("/quotes/<int:id>")
def get_quote_id(id):
    quote = db.session.get(QuoteModel, id)   
    if not quote is None:
        return jsonify(quote.to_dict()), 200
    abort(404, f"Quote id = {id} not found")


# POST на url: /quotes/
@app.post("/quotes")
def create_quote():
    new_quote = request.json
    if new_quote.get("author") and new_quote.get("text"):
        new_row = QuoteModel(new_quote.get("author"), new_quote.get("text"), new_quote.get("rating"))
        db.session.add(new_row)
        db.session.commit()
        print(new_row.to_dict())
        return jsonify(new_row.to_dict()), 200
    abort(400, "NOT NULL constraint failed")


# PUT на url: /quotes/<int:id>
@app.put("/quotes/<int:id>")
def edit_quote(id):
    new_data = request.json
    quote = db.session.get(QuoteModel, id) 
    if not quote is None:
        if not new_data.get("author") is None:
            quote.author = new_data.get("author")
        if not new_data.get("text") is None:
            quote.text = new_data.get("text")
        if not new_data.get("rating") is None and 0 < new_data.get("rating") < 6:
            quote.rating = new_data.get("rating")
        db.session.commit()
        return jsonify(quote.to_dict()), 200
    abort(404, f"Quote id = {id} not found")


# DELETE на url: /quotes/<int:id>
@app.delete("/quotes/<int:id>")
def delete(id):
    quote = db.session.get(QuoteModel, id)
    if not quote is None:
        db.session.delete(quote)
        db.session.commit()
        return {"message": f"Row with id={id} deleted."}, 200
    abort(404, f"Quote id = {id} not found")
    

# GET filter
@app.get("/quotes/filter")
def get_quote_by_filter():
    kwargs = request.args
    quotes = QuoteModel.query.filter_by(**kwargs).all()
    quotes_lst = []
    if quotes:
        for quote in quotes:
            quotes_lst.append(quote.to_dict())
        return jsonify(quotes_lst), 200
    return jsonify([]), 200



if __name__ == "__main__":
   app.run(debug=True)