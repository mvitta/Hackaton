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
ruta_db = "orion1_db.db"


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
    if request.method == "POST":
        nombre = request.form.get('Nombre')
        correo = request.form.get('Correo')
        sexo = request.form.get('flexRadioDefault')
        nacimiento = request.form.get('fecha')
        direccion = request.form.get('direccion')
        ciudad = request.form.get('ciudad')
        nombre_usuario = request.form.get('nombreUsuario')
        password = request.form.get('Contra')
        apellido = request.form.get('Apellido')
        cedula = request.form.get('Cedula')
        try:
            conexion = conexionBaseDeDatos()
            cur = conexion.cursor()
            sql = "INSERT INTO tb_users (nombre, correo, sexo, nacimiento, direccion, ciudad, acumulado_compras, num_bonos, nombre_usuario, password, rol, apellido, cedula) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(sql, [nombre, correo, sexo, nacimiento, direccion, ciudad,
                        0, 0, nombre_usuario, password, "comprador", apellido, cedula])
            conexion.commit()
            cur.close()
            return render_template("registro.html")
        except Error as err:
            print(err)
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
        return render_template("dashboardProducto.html", registrosProductos=registrosProductos)
    except Error:
        print(Error)
        return render_template("error !!!  :| ")


@app.route('/dashboardLotes')
def dashboardLotes():
    try:
        conexion = conexionBaseDeDatos()
        cur = conexion.cursor()
        sql = "SELECT p.id_producto, p.nombre_producto, l.id_lote, lp.cantidad, lp.fecha_entrada, lp.fecha_salida FROM tb_lotes l, tb_productos p, tb_lotes_productos lp WHERE l.id_lote = lp.id_lote_producto AND p.id_producto = lp.id_producto"
        cur.execute(sql)
        conexion.commit()
        registrosLotesProductos = cur.fetchall()
        cur.close()
        return render_template('dashboardLotes.html', registrosLotesProductos= registrosLotesProductos)
    except Error:
        print(Error)
        return render_template("error !!!  :| ")

@app.route('/dashboardProductosVendidos')
def dashboardProductosVendidos():
    return render_template('dashboardProductosVendidos.html')


@app.route('/dashboardUsuariosRegistrados')
def dashboardUsuariosRegistrados():
    try:
        conexion = conexionBaseDeDatos()
        cur = conexion.cursor()
        sql = "SELECT * FROM tb_users"
        cur.execute(sql)
        conexion.commit()
        registrosUsuarios = cur.fetchall()
        cur.close()
        print(registrosUsuarios)
        return render_template("dashboardUsuariosRegistrados.html", registrosUsuarios=registrosUsuarios)
    except Error:
        print(Error)
        
    


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
