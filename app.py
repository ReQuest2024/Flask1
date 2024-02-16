from flask import Flask, abort, jsonify, request
import random
from pathlib import Path
from werkzeug.exceptions import HTTPException
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class QuoteModel(db.Model):
    __tablename__ = "quote_model"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False, nullable=False)
    text = db.Column(db.String(255), unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, author, text, rating):
       self.author = author
       self.text  = text
       self.rating = rating if rating is not None and 0 < rating < 6 else 1

    def __repr__(self):
        return f'Quote({self.author}, {self.text}, {self.rating})'

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text,
            "rating": self.rating
        }

# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


# GET на url: /quotes/
@app.route("/quotes")
def get_quotes():
    quotes_lst = db.session.query(QuoteModel)   # QuoteModel.query.all()
    quotes_lst_dct = []
    for quote in quotes_lst:
        quotes_lst_dct.append(quote.to_dict())
    return jsonify(quotes_lst_dct), 200


# GET на url: /quotes/<int:id>
@app.get("/quotes/<int:id>")
def get_quote_id(id):
    quote = db.session.get(QuoteModel, id)      # The Query.get() method is considered legacy (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
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
    




if __name__ == "__main__":
   app.run(debug=True)