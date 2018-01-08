
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import DevConfig


app = Flask(__name__)
app.config.from_object(DevConfig)

db = SQLAlchemy(app)


@app.route("/")
def home():
    return "<h1>Hello World!</h1>"


if __name__ == '__main__':
    app.run()
