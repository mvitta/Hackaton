from logging import debug, error
from sqlite3.dbapi2 import Cursor
from flask import Flask, render_template, request, flash, session, redirect
import os
from flask import *
import sqlite3
from sqlite3 import Error
import base64
from markupsafe import escape
import hashlib
from werkzeug.exceptions import UnsupportedMediaType
from werkzeug.security import generate_password_hash, check_password_hash


ruta_index = "index.html"
ruta_productos = "productos.html"
ruta_db = "orion_db.db"


app = Flask(__name__)
app.secret_key = os.urandom(34)


def conexionBaseDeDatos():
    db = getattr(g, '_database_USUARIO', None)
    if db is None:
        db = g._database_USUARIO = sqlite3.connect(ruta_db)
    return db


@app.route('/', methods=['POST', 'GET'])
def login():
    return render_template('login.html')


@app.route('/registro', methods=['POST', 'GET'])
def registro():
    return render_template('registro.html')


@app.route('/dashboarProductos')
def dashboardProductos():
    try:
        conexion = conexionBaseDeDatos()
        cur = conexion.cursor()
        sql = "SELECT * FROM tb_productos"
        cur.execute(sql)
        conexion.commit()
        registrosProductos = cur.fetchall()
        cur.close()
        print(registrosProductos)
        return render_template("dashboardProducto.html", registrosProductos=registrosProductos)
    except Error:
        print(Error)
        return render_template("error !!!  :| ")


@app.route('/dashboardLotes')
def dashboardLotes():
    return render_template('dashboardLotes.html')


@app.route('/dashboardProductosVendidos')
def dashboardProductosVendidos():
    return render_template('dashboardProductosVendidos.html')


@app.route('/dashboardUsuariosRegistrados')
def dashboardUsuariosRegistrados():
    return render_template('dashboardUsuariosRegistrados.html')


@app.route('/dashboardComentariosUsuarios')
def dashboardComentariosUsuarios():
    return render_template('dashboardComentariosUsuarios.html')


@app.route('/producto/<string:id>', methods=['POST', 'GET'])
def producto(id=None):
    try:
        with sqlite3.connect(ruta_db) as con:
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM productos WHERE codigo_producto=?", [id])
            row_producto = cur.fetchone()

            return render_template('baseProducto.html', row_producto=row_producto)
    except Error:
        print(Error)
        return render_template(ruta_productos)


@app.route("/productos")
def productos():
    try:
        with sqlite3.connect(ruta_db) as con:
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM productos LIMIT 4")
            row_productos = cur.fetchall()

            return render_template(ruta_productos, row_productos=row_productos)
    except Error:
        print(Error)
        return render_template(ruta_productos)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
