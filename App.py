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


compExitosa = "compraExitosa.html"
ruta_perfil="perfil.html"
ruta_index = "index.html"
ruta_productos = "productos.html"
ruta_login = "login.html"
ruta_producto = "baseProducto.html"
ruta_db = "orion1_db.db"


app = Flask(__name__)
app.secret_key = os.urandom(34)


def conexionBaseDeDatos():
    db = getattr(g, '_database_USUARIO', None)
    if db is None:
        db = g._database_USUARIO = sqlite3.connect(ruta_db)
    return db


@app.route('/', methods=['POST', 'GET'])
def index():
    if "usuario" in session:
        inicio = 1
        rol = session["rol"]
        id=session["usuario"]
        
    else:
        inicio = 0
        rol = 0
        id=0

    return render_template(ruta_index, inicio=inicio, rol=rol,id=id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = escape(request.form["usuario"])
        password = escape(request.form["contra"])
        try:
            with sqlite3.connect(ruta_db) as con:
                cur = con.cursor()
                cur.execute(
                    "SELECT password FROM tb_users WHERE correo=?", [correo])
                row = cur.fetchone()
                if row is None:
                    return "Usuario no se encuentra en la base de datos"
                else:
                    if check_password_hash(row[0], password):
                        session["usuario"] = correo
                        session["rol"] = "comprador"

                        return redirect("/")
                    else:
                        return render_template(ruta_index, rol=session["rol"])
        except Error:
            print(Error)
    return render_template(ruta_login)


@app.route("/loginUsuarioInterno", methods=["GET", "POST"])
def loginUsuarioInterno():
    if request.method == "POST":
        usuario = escape(request.form["usuario"])
        password = escape(request.form["contra"])
        print(usuario)
        print(password)
        try:
            with sqlite3.connect(ruta_db) as con:
                cur = con.cursor()
                cur.execute(
                    "SELECT rol FROM tb_empleados WHERE nombre_usuario=?", [usuario])
                rol1 = cur.fetchone()
                rol = rol1[0]
                print(rol)
                cur = con.cursor()
                cur.execute(
                    "SELECT password FROM tb_empleados WHERE nombre_usuario=?", [usuario])
                row = cur.fetchone()
                print(row)

                if row is None:
                    return "Usuario no se encuentra en la base de datos"
                else:
                    if check_password_hash(row[0], password):
                        session["usuario"] = usuario
                        session["rol"] = rol
                        print(session["rol"])
                        print(rol)

                        return render_template("index.html", rol=rol, inicio=1)
                    else:
                        return "Contraseña incorrecta"
        except Error:
            print(Error)
    return render_template("loginUsuarioInterno.html")


@app.route("/loginSuperAdministrador", methods=["GET", "POST"])
def loginSuperAdministrador():
    return render_template("loginSuperAdministrador.html")


@app.route('/registro', methods=['POST', 'GET'])
def registro():
    if request.method == "POST":
        nombre = escape(request.form.get('Nombre'))
        correo = escape(request.form.get('Correo'))
        sexo = escape(request.form.get('flexRadioDefault'))
        nacimiento = escape(request.form.get('fecha'))
        direccion = escape(request.form.get('direccion'))
        ciudad = escape(request.form.get('ciudad'))
        nombre_usuario = escape(request.form.get('nombreUsuario'))
        password = escape(request.form.get('Contra'))
        hash = generate_password_hash(password)
        apellido = escape(request.form.get('Apellido'))
        cedula = escape(request.form.get('Cedula'))
        try:
            conexion = conexionBaseDeDatos()
            cur = conexion.cursor()
            sql = "INSERT INTO tb_users (id_user,nombre, correo, sexo, nacimiento, direccion, ciudad, acumulado_compras, num_bonos, nombre_usuario, password, rol, apellido) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(sql, [cedula, nombre, correo, sexo, nacimiento, direccion, ciudad,
                        0, 0, nombre_usuario, hash, "comprador", apellido])
            conexion.commit()
            cur.close()
            return render_template("login.html")
        except Error as err:
            print(err)
    return render_template('registro.html')


@app.route('/dashboarProductos')
def dashboardProductos():
    if "usuario" in session:
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
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardCrearProducto',  methods=['POST', 'GET'])
def dashboardCrearProducto():
    if "usuario" in session:
        if request.method == "POST":
            valores = []
            names = ['nombreProducto', 'categoria', 'areaTexto',
                     'tipoUnidad', 'precioProducto', 'unidades', 'procentajePromo', 'valorVenta', 'bonoDescuento', 'totalUnidades']
            for i in names:
                valores.append(request.form.get(i))

            imagen = request.files["imagen"]
            imagenBinario = base64.b64encode(imagen.read())
            imagenBinario_ = imagenBinario.decode("utf-8")
            try:
                conexion = conexionBaseDeDatos()
                cur = conexion.cursor()
                sql = "INSERT INTO tb_productos (nombre_producto, categoria, descripcion, tipo_unidad, precio_unidad, unidades_vendidas, porcentaje_promo, valor_ventas, bono_descuento, calificacion_producto, imagen, total_unidades) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cur.execute(sql, [valores[0], valores[1], valores[2], valores[3], valores[4], valores[5], valores[6],
                            valores[7], valores[8], 0, imagenBinario_, valores[9]])
                conexion.commit()
                cur.close()
                return render_template("dashboardCrearProducto.html")
            except Error as err:
                print(err)
    else:
        return "Por favor inicie sesion"
    return render_template("dashboardCrearProducto.html")


@app.route('/dashboardLotes')
def dashboardLotes():
    if "usuario" in session:
        try:
            conexion = conexionBaseDeDatos()
            cur = conexion.cursor()
            sql = "SELECT p.id_producto, p.nombre_producto, l.id_lote, lp.cantidad, lp.fecha_entrada, lp.fecha_salida FROM tb_lotes l, tb_productos p, tb_lotes_productos lp WHERE l.id_lote = lp.id_lote_producto AND p.id_producto = lp.id_producto"
            cur.execute(sql)
            conexion.commit()
            registrosLotesProductos = cur.fetchall()
            cur.close()
            return render_template('dashboardLotes.html', registrosLotesProductos=registrosLotesProductos)
        except Error:
            print(Error)
            return render_template("error !!!  :| ")
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardProductosVendidos')
def dashboardProductosVendidos():
    if "usuario" in session:
        return render_template('dashboardProductosVendidos.html')
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardUsuariosRegistrados')
def dashboardUsuariosRegistrados():
    if "usuario" in session:
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
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardComentariosUsuarios')
def dashboardComentariosUsuarios():
    if "usuario" in session:
        try:
            conexion = conexionBaseDeDatos()
            cur = conexion.cursor()
            sql = "SELECT * FROM tb_comentario"
            cur.execute(sql)
            conexion.commit()
            registrosComentarios = cur.fetchall()
            cur.close()
            return render_template('dashboardComentariosUsuarios.html', registrosComentarios=registrosComentarios)
        except Error:
            print(Error)
            return render_template("error !!!  :| ")
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardRegistrarUsuarioInterno', methods=['POST', 'GET'])
def dashboardRegistrarUsuarioInterno():
    if "usuario" in session:
        if request.method == "POST":
            nombre = escape(request.form.get('Nombre'))
            correo = escape(request.form.get('Correo'))
            sexo = escape(request.form.get('flexRadioDefault'))
            nacimiento = escape(request.form.get('fecha'))
            cargo = escape(request.form.get('cargo'))
            direccion = escape(request.form.get('direccion'))
            ciudad = escape(request.form.get('ciudad'))
            nombre_usuario = escape(request.form.get('nombreUsuario'))
            password = escape(request.form.get('Contra'))
            hash = generate_password_hash(password)
            apellido = escape(request.form.get('Apellido'))
            cedula = escape(request.form.get('Cedula'))

            try:
                conexion = conexionBaseDeDatos()
                cur = conexion.cursor()
                sql = "INSERT INTO tb_empleados (id_empleado,cedula,nombre, apellido,cargo, sexo, fecha_nacimiento, direccion, ciudad, nombre_usuario, password, rol) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cur.execute(sql, [cedula, cedula, nombre, apellido, cargo, sexo,
                            nacimiento, direccion, ciudad, nombre_usuario, hash, "interno"])
                conexion.commit()
                cur.close()
                return render_template("dashboardRegistrarUsuarioInterno.html")
            except Error as err:
                print(err)

        return render_template('dashboardRegistrarUsuarioInterno.html')
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardRegistrosUsuariosInternos', methods=['GET'])
def dashboardRegistrosUsuariosInternos():
    if "usuario" in session:
        try:
            conexion = conexionBaseDeDatos()
            cur = conexion.cursor()
            sql = "SELECT * FROM tb_empleados"
            cur.execute(sql)
            conexion.commit()
            registrosUsuariosInternos = cur.fetchall()
            cur.close()
            print(registrosUsuariosInternos)
            return render_template('dashboardRegistrosUsuariosInternos.html', registrosUsuariosInternos=registrosUsuariosInternos)
        except Error:
            print(Error)
    else:
        return "Por favor inicie sesion"


@app.route('/producto/<string:id_producto>', methods=['POST', 'GET'])
def producto(id_producto=None):
    if "usuario" in session:
        inicio = 1
        rol = session["rol"]
        id=session["usuario"]
    else:
        inicio = 0
        rol = 0
        id=0
    try:
        with sqlite3.connect(ruta_db) as con:
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM tb_productos WHERE id_producto=?", [id_producto])
            row_producto = cur.fetchone()
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM tb_comentario WHERE id_producto=?", [id_producto])
            row_comentarios = cur.fetchall()
            print(row_producto)
            print(row_comentarios)

            return render_template('baseProducto.html', row_producto=row_producto, row_comentarios=row_comentarios, inicio=inicio, rol=rol,id=id)
    except Error:
        print(Error)
        return render_template(ruta_productos, inicio=inicio, rol=rol,id=id)


@app.route("/productos")
def productos():
    if "usuario" in session:
        inicio = 1
        rol = session["rol"]
        id=session["usuario"]
    else:
        inicio = 0
        rol = 0
        id=0
    try:
        with sqlite3.connect(ruta_db) as con:
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM tb_productos")
            row_productos = cur.fetchall()

            return render_template(ruta_productos, row_productos=row_productos, inicio=inicio, rol=rol,id=id)
    except Error:
        print(Error)
        return render_template(ruta_productos, inicio=inicio, rol=rol,id=id)


@app.route("/comentar/<string:id>", methods=["GET", "POST"])
def comentar(id=None):
    if request.method == "POST":
        if "usuario" in session:
            inicio = 1
            try:
                with sqlite3.connect(ruta_db) as con:
                    print("Entro")
                    comentario = escape(request.form["comentario"])
                    calificacion = escape(request.form["puntuacion"])
                    cur = con.cursor()
                    cur.execute("INSERT INTO tb_comentario(usuario, comentario,id_producto,calificacion) VALUES (?,?,?,?)", (
                        session["usuario"], comentario, id, calificacion))
                    con.commit()
                    print("Si lo hizo")
                    con.row_factory = sqlite3.Row
                    cur = con.cursor()
                    cur.execute(
                        "SELECT * FROM tb_comentario WHERE id_producto=?", [id])
                    print("si lo hizo")
                    row_comentarios = cur.fetchall()
                    print(row_comentarios)
                    cur = con.cursor()
                    cur.execute(
                        "SELECT avg(calificacion) from tb_comentario where id_producto=?", [id])
                    print("si lo hizo")
                    row = cur.fetchone()

                    promedio = row[0]
                    cur = con.cursor()
                    cur.execute(
                        "update tb_productos SET calificacion_producto=? where id_producto=?", (promedio, id))
                    print("si lo hizo")
                    con.commit()
                    cur = con.cursor()
                    con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
                    cur = con.cursor()
                    cur.execute(
                        "SELECT * FROM tb_productos WHERE id_producto=?", [id])
                    print("si lo hizo")
                    row_producto = cur.fetchone()
                    return render_template(ruta_producto, row_producto=row_producto, row_comentarios=row_comentarios, inicio=inicio, id=session["usuario"])
            except Error:
                print(Error)
        else:
            return "Debe iniciar sesion para poder comentar"
    return "Metodo erroneo"


@app.route("/logout")
def logout():
    if "usuario" in session:
        session.pop("usuario", None)
        return render_template(ruta_index, inicio=0)
    else:
        return "No hay sesion activa"


@app.route("/compraExitosa")
def compraExitosa():
    # if "usuario" in session:
    #     session.pop("usuario", None)
    return render_template(compExitosa)
    # else:
    #     return "No hay sesion activa"

@app.route("/perfil/<string:id>", methods=["GET","POST"])
def perfil(id=id):
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con: 
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM tb_users WHERE correo=?",[id])
                row_perfil = cur.fetchone()
                rol=session["rol"]
                con.row_factory = sqlite3.Row #Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM tb_comentario WHERE usuario=?",[session["usuario"]])
                row_comentarios = cur.fetchall()
                return render_template(ruta_perfil,row_usuario=row_perfil,rol=rol,row_comentarios=row_comentarios,inicio=1,id=session["usuario"])
        except Error:
            print(Error)
    return "Debe iniciar sesion"


if __name__ == "__main__":
    app.run(debug=True, port=8000)
