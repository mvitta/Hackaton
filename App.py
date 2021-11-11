from logging import debug, error
from sqlite3.dbapi2 import Cursor
from flask import Flask, render_template, request, flash,session,redirect
import os
from flask import *
import sqlite3
from sqlite3 import Error
import base64
from markupsafe import escape 
import hashlib
from werkzeug.exceptions import UnsupportedMediaType
from werkzeug.security import generate_password_hash, check_password_hash


ruta_index="index.html"

app = Flask(__name__)
app.secret_key = os.urandom(34)


@app.route('/')
def index():
    return render_template(ruta_index)



if __name__ == "__main__":
    app.run(debug=True, port=8000)