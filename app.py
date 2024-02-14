from flask import Flask, request, jsonify, g
import random
import sqlite3
from pathlib import Path
from werkzeug.exceptions import HTTPException

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"  # <- path to DB


app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

    db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher’s Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]

for quote in quotes:
    quote["rating"] = random.choice(range(3,6))

@app.route("/")
def hello_world():
   return "Hello, World!"

@app.route("/about")
def about():
    about_me = {
                "name": "Name",
                "surname": "Surename",
                "email": ""
                }
    return about_me

@app.get("/quotes")
def get_quotes():
    # Получение данных из БД
    select_quotes = "SELECT * from quotes"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall()  
    cursor.close()
    if quotes_db:
        return quotes_db, 200
    else:
        return "Not found.", 404

@app.get("/quotes/<int:id>")
def quote_id(id):
    select_quotes = f"SELECT * from quotes WHERE id = {id}"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    quote = cursor.fetchone() 
    cursor.close()
    if quote:
        return quote, 200
    else:
        return f"Quote with id={id} not found.", 404
    
   
@app.route("/quotes/count")
def quotes_count():
   return {"count":len(quotes)}, 200

@app.route("/quotes/random")
def quotes_random():
   return random.choice(quotes), 200



def new_id():
    return quotes[-1]["id"] + 1

# methods POST
@app.post("/quotes")
def create_quote():
    new_quote = request.json
    create_quote = "INSERT INTO quotes (author,text) VALUES (?, ?)"
    cursor = get_db().cursor()
    param = (new_quote.get("author") if new_quote.get("author") else ""
            , new_quote.get("text") if new_quote.get("text") else ""
            )
    cursor.execute(create_quote, param)
    new_id = cursor.lastrowid
    g._database.commit()
    if new_id:
        return quote_id(new_id)
    else:
        return {}, 500

# methods PUT
@app.put("/quotes/<int:id>")
def edit_quote(id):
    new_data = request.json
    cursor = get_db().cursor()
    edit_quote = ""
    resp = 0
    param = []
    if new_data.get("author") or new_data.get("text"):
        if new_data.get("author"):
            edit_quote += "author=?"
            param.append(new_data["author"])
        if new_data.get("author") and new_data.get("text"):
            edit_quote += ", "
        if new_data.get("text"):
            edit_quote += "text=?"
            param.append(new_data["text"])
        param.append(id)
        edit_quote = f'UPDATE quotes SET {edit_quote} WHERE id=?'
        print(edit_quote)
        cursor.execute(edit_quote, param)
        resp = cursor.rowcount

        g._database.commit()
    cursor.close()
    if resp:
        return quote_id(id)
    else:
        return {}, 500

# methods DELETE    
@app.delete("/quotes/<int:id>")
def delete(id):
    cursor = get_db().cursor()
    delete_quote = f'DELETE FROM quotes WHERE id={id}'
    print(delete_quote)
    cursor.execute(delete_quote)
    resp = cursor.rowcount

    g._database.commit()
    cursor.close()
    
    if resp:
        return f"Row with id={id} deleted.", 200
    else:
        return f"Row with id={id} not found.", 404


if __name__ == "__main__":
   app.run(debug=True)