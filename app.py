from flask import Flask
import random
from flask import request

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

about_me = {
   "name": "Name",
   "surname": "Surname",
   "email": "email"
}

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

@app.route("/")
def hello_world():
   return "Hello, World!"

@app.route("/about")
def about():
   return about_me

@app.route("/quotes")
def quotes_lst():
   return quotes

@app.route("/quotes/<int:id>")
def quote_id(id):
   for quote in quotes:
      if quote["id"] == id:
         return quote, 200
   return f"Quote with id={id} not found", 404
   
@app.route("/quotes/count")
def quotes_count():
   return {"count":len(quotes)}, 200

@app.route("/quotes/random")
def quotes_random():
   return random.choice(quotes), 200

@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   print("data = ", data)
   return {}, 201

if __name__ == "__main__":
   app.run(debug=True)
