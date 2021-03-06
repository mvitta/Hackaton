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
ruta_perfil = "perfil.html"
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


def handle_cart():
    products = []
    grand_total = 0
    index = 0
    quantity_total = 0
    print(1)
    print(session["cart"])
    for item in session['cart']:
        print(2)
        try:
            with sqlite3.connect(ruta_db) as con:
                con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                print(item["id"])
                cur.execute(
                    "SELECT * FROM tb_productos WHERE id_producto=?", [item["id"]])
                product = cur.fetchone()
                print("producto")
                print(product)
        except:
            print("error")
        quantity = int(item['cantidad'])
        total = quantity * product["precio_unidad"]
        grand_total += total

        quantity_total += quantity
        print(3)

        products.append({'id': product["id_producto"], 'nombre': product["nombre_producto"], 'precio':  product["precio_unidad"],
                         'imagen': product["imagen"], 'cantidad': quantity, 'total': total, 'index': index})
        index += 1
        print(4)

    return products, grand_total, quantity_total


@app.route('/', methods=['POST', 'GET'])
def index():
    if "usuario" in session:
        inicio = 1
        rol = session["rol"]
        id = session["usuario"]

    else:
        inicio = 0
        rol = 0
        id = 0

    return render_template(ruta_index, inicio=inicio, rol=rol, id=id)


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
                        session["cart"] = []

                        return redirect("/")
                    else:
                        return "Contrase??a incorrecta"
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
                        return "Contrase??a incorrecta"
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
        nombre=nombre.lower()
        correo = escape(request.form.get('Correo'))
        sexo = escape(request.form.get('flexRadioDefault'))
        nacimiento = escape(request.form.get('fecha'))
        direccion = escape(request.form.get('direccion'))
        ciudad = escape(request.form.get('ciudad'))
        nombre_usuario = escape(request.form.get('nombreUsuario'))
        password = escape(request.form.get('Contra'))
        hash = generate_password_hash(password)
        apellido = escape(request.form.get('Apellido'))
        apellido=apellido.lower()
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


def obtenerNombreProductos():
    conexion = conexionBaseDeDatos()
    cur = conexion.cursor()
    sql = "SELECT nombre_producto FROM tb_productos"
    cur.execute(sql)
    conexion.commit()
    nombreProductos = cur.fetchall()
    cur.close()
    return nombreProductos


@app.route('/dashboarProductos', methods=['POST', 'GET'])
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
            # mostrar por consola para ver el comportamiento
            for registro in registrosProductos:
                r = list(registro)
                r.pop(len(r) - 2)
                print(r)
            if request.method == 'POST':
                if request.form.get('ordenarVentas') == 'ordenar por mayor ventas':
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos ORDER BY unidades_vendidas DESC"
                    cur.execute(sql)
                    conexion.commit()
                    registrosOrdenadosPorVentas = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosOrdenadosPorVentas, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('ordenarExistentes') == 'ordenar cantidades existentes':
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos ORDER BY total_unidades ASC"
                    cur.execute(sql)
                    conexion.commit()
                    registrosOrdenadosPorExistentes = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosOrdenadosPorExistentes, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('filtrarCategoriaBaja') == 'filtrar por categoria baja':
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos WHERE categoria=?"
                    cur.execute(sql, ['Baja'])
                    conexion.commit()
                    registrosCategoriaBaja = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosCategoriaBaja, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('filtrarCategoriaMedia') == 'filtrar por categoria media':
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos WHERE categoria=?"
                    cur.execute(sql, ['Media'])
                    conexion.commit()
                    registrosCategoriaMedia = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosCategoriaMedia, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('filtrarCategoriaAlta') == 'filtrar por categoria alta':
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos WHERE categoria=?"
                    cur.execute(sql, ['Alta'])
                    conexion.commit()
                    registrosCategoriaAlta = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosCategoriaAlta, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('productosDescuento') == 'Productos con descuento':
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos WHERE bono_descuento=?"
                    cur.execute(sql, ['si'])
                    conexion.commit()
                    registrosBonoDescuento = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosBonoDescuento, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('rangoPrecio') == 'Rango de precio':
                    min = request.form.get('min')
                    max = request.form.get('max')
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos WHERE valor_ventas BETWEEN ? AND ?"
                    cur.execute(sql, [min, max])
                    conexion.commit()
                    registrosPorRangoPrecio = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosPorRangoPrecio, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('buscarProducto') == 'Buscar Producto':
                    pro = request.form.get('productos')
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos WHERE nombre_producto=?"
                    cur.execute(sql, [str(pro)])
                    conexion.commit()
                    registrosPorNombreProducto = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosPorNombreProducto, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('eliminar') == 'eliminar':
                    id_pro = request.form.get('seleccionar')
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "DELETE FROM tb_productos WHERE id_producto=?"
                    cur.execute(sql, [id_pro])
                    conexion.commit()

                    sql = "SELECT * FROM tb_productos"
                    cur.execute(sql)
                    conexion.commit()
                    registrosProductoEliminado = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosProductoEliminado, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

                if request.form.get('editar') == 'editar':
                    actualizar = True
                    session['id_producto'] = request.form.get('seleccionar')
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_productos WHERE id_producto=?"
                    cur.execute(sql, session['id_producto'])
                    conexion.commit()
                    registrosProductoPorID = cur.fetchall()
                    cur.close()
                    return render_template("dashboardProducto.html", registrosProductos=registrosProductos, nombreProductos=obtenerNombreProductos(), actualizar=actualizar, registrosProductoPorID=registrosProductoPorID,rol="interno", inicio=1)

                if request.form.get('confirmar') == 'confirmar':
                    nombreProducto = request.form.get('op1')
                    categoria = request.form.get('op2')
                    descrip = request.form.get('op3')
                    tipoUnidad = request.form.get('op4')
                    precioUnidad = request.form.get('op5')
                    unidadesVendidas = request.form.get('op6')
                    porcePromo = request.form.get('op7')
                    valorVentas = request.form.get('op8')
                    bonoDescuento = request.form.get('op9')
                    califProducto = request.form.get('op10')
                    totalUnidades = request.form.get('op12')
                
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "UPDATE tb_productos SET nombre_producto=?, categoria=?, descripcion=?, tipo_unidad=?, precio_unidad=?, unidades_vendidas=?, porcentaje_promo=?, valor_ventas=?, bono_descuento=?, calificacion_producto=?, total_unidades=? WHERE id_producto=? "
                    cur.execute(sql, [nombreProducto, categoria, descrip, tipoUnidad, precioUnidad, unidadesVendidas,
                                porcePromo, valorVentas, bonoDescuento, califProducto, totalUnidades, session['id_producto']])
                    conexion.commit()

                    sql = "SELECT * FROM tb_productos"
                    cur.execute(sql)
                    conexion.commit()
                    registrosProductoEditado = cur.fetchall()
                    cur.close()
                return render_template("dashboardProducto.html", registrosProductos=registrosProductoEditado, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)

            return render_template("dashboardProducto.html", registrosProductos=registrosProductos, nombreProductos=obtenerNombreProductos(),rol="interno", inicio=1)
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
    return render_template("dashboardCrearProducto.html",rol="interno", inicio=1)


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
            return render_template('dashboardLotes.html', registrosLotesProductos=registrosLotesProductos,rol="interno", inicio=1)
        except Error:
            print(Error)
            return render_template("error !!!  :| ")
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardProductosVendidos')
def dashboardProductosVendidos():
    if "usuario" in session:
        return render_template('dashboardProductosVendidos.html',rol="interno", inicio=1)
    else:
        return "Por favor inicie sesion"


@app.route('/dashboardUsuariosRegistrados',  methods=['POST', 'GET'])
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

            if request.method == 'POST':
                if request.form.get('buscar') == 'Buscar':
                    usuario = request.form.get('buscador')
                    print(usuario)
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_users WHERE nombre=?"
                    cur.execute(sql, [str(usuario)])
                    conexion.commit()
                    registrosUsuario = cur.fetchall()
                    cur.close()
                    return render_template("dashboardUsuariosRegistrados.html", registrosUsuarios=registrosUsuario)

                if request.form.get('eliminar') == 'eliminar':
                    id_user = request.form.get('seleccionar')
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "DELETE FROM tb_users WHERE id_user=?"
                    cur.execute(sql, [id_user])
                    conexion.commit()

                    sql = "SELECT * FROM tb_users"
                    cur.execute(sql)
                    conexion.commit()
                    registrosUsuario = cur.fetchall()
                    cur.close()
                    return render_template("dashboardUsuariosRegistrados.html", registrosUsuarios=registrosUsuario)

            return render_template("dashboardUsuariosRegistrados.html", registrosUsuarios=registrosUsuarios,rol="interno", inicio=1)

        except Error:
            print(Error)
    else:
        return "Por favor inicie sesion"


@ app.route('/dashboardComentariosUsuarios')
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

            if request.form.get('eliminar') == 'eliminar':
                id_comen = request.form.get('seleccionar')
                conexion = conexionBaseDeDatos()
                cur = conexion.cursor()
                sql = "DELETE FROM tb_comentario WHERE id_comentario=?"
                cur.execute(sql, [id_comen])
                conexion.commit()

                sql = "SELECT * FROM tb_empleados"
                cur.execute(sql)
                conexion.commit()
                registrosComentariosEliminados = cur.fetchall()
                cur.close()
                return render_template('dashboardComentariosUsuarios.html', registrosComentarios=registrosComentariosEliminados,rol="interno", inicio=1)

            return render_template('dashboardComentariosUsuarios.html', registrosComentarios=registrosComentarios,rol="interno", inicio=1)
        except Error:
            print(Error)
            return render_template("error !!!  :| ")
    else:
        return "Por favor inicie sesion"


@ app.route('/dashboardRegistrarUsuarioInterno', methods=['POST', 'GET'])
def dashboardRegistrarUsuarioInterno():
    if "usuario" in session:
        if request.method == "POST":
            nombre = escape(request.form.get('Nombre'))
            nombre=nombre.lower()
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
            apellido=apellido.lower()
            cedula = escape(request.form.get('Cedula'))

            try:
                conexion = conexionBaseDeDatos()
                cur = conexion.cursor()
                sql = "INSERT INTO tb_empleados (id_empleado,cedula,nombre, apellido,cargo, sexo, fecha_nacimiento, direccion, ciudad, nombre_usuario, password, rol) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cur.execute(sql, [cedula, cedula, nombre, apellido, cargo, sexo,
                            nacimiento, direccion, ciudad, nombre_usuario, hash, "interno"])
                conexion.commit()
                cur.close()
                return render_template("dashboardRegistrarUsuarioInterno.html",rol="interno", inicio=1)
            except Error as err:
                print(err)

        return render_template('dashboardRegistrarUsuarioInterno.html',rol="interno", inicio=1)
    else:
        return "Por favor inicie sesion"


@ app.route('/dashboardRegistrosUsuariosInternos', methods=['GET', 'POST'])
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

            if request.method == 'POST':
                if request.form.get('buscar') == 'Buscar':
                    usuarioInterno = request.form.get('buscadorInterno')
                    print(usuarioInterno)
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "SELECT * FROM tb_empleados WHERE nombre=?"
                    cur.execute(sql, [str(usuarioInterno)])
                    conexion.commit()
                    registrosUsuariosInternos = cur.fetchall()
                    cur.close()
                    return render_template('dashboardRegistrosUsuariosInternos.html', registrosUsuariosInternos=registrosUsuariosInternos,rol="interno", inicio=1)

                if request.form.get('eliminar') == 'eliminar':
                    id_empl = request.form.get('seleccionar')
                    conexion = conexionBaseDeDatos()
                    cur = conexion.cursor()
                    sql = "DELETE FROM tb_empleados WHERE id_empleado=?"
                    cur.execute(sql, [id_empl])
                    conexion.commit()

                    sql = "SELECT * FROM tb_empleados"
                    cur.execute(sql)
                    conexion.commit()
                    registrosUsuariosInternosEliminado = cur.fetchall()
                    cur.close()
                    return render_template('dashboardRegistrosUsuariosInternos.html', registrosUsuariosInternos=registrosUsuariosInternosEliminado,rol="interno", inicio=1)
            return render_template('dashboardRegistrosUsuariosInternos.html', registrosUsuariosInternos=registrosUsuariosInternos,rol="interno", inicio=1)
        except Error:
            print(Error)
    else:
        return "Por favor inicie sesion"


@ app.route('/producto/<string:id_producto>', methods=['POST', 'GET'])
def producto(id_producto=None):
    if "usuario" in session:
        inicio = 1
        rol = session["rol"]
        id = session["usuario"]
    else:
        inicio = 0
        rol = 0
        id = 0
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

            return render_template('baseProducto.html', row_producto=row_producto, row_comentarios=row_comentarios, inicio=inicio, rol=rol, id=id)
    except Error:
        print(Error)
        return render_template(ruta_productos, inicio=inicio, rol=rol, id=id)


@ app.route("/productos")
def productos():
    if "usuario" in session:
        inicio = 1
        rol = session["rol"]
        id = session["usuario"]
    else:
        inicio = 0
        rol = 0
        id = 0
    try:
        with sqlite3.connect(ruta_db) as con:
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM tb_productos")
            row_productos = cur.fetchall()

            return render_template(ruta_productos, row_productos=row_productos, inicio=inicio, rol=rol, id=id)
    except Error:
        print(Error)
        return render_template(ruta_productos, inicio=inicio, rol=rol, id=id)


@ app.route("/comentar/<string:id>", methods=["GET", "POST"])
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


@ app.route("/logout")
def logout():
    if "usuario" in session:
        session.pop("usuario", None)
        return render_template(ruta_index, inicio=0)
    else:
        return "No hay sesion activa"


@ app.route("/compraExitosa")
def compraExitosa():
    # if "usuario" in session:
    #     session.pop("usuario", None)
    return render_template(compExitosa, inicio=1, rol=0, id=session["usuario"])
    # else:
    #     return "No hay sesion activa"


@ app.route("/perfil/<string:id>", methods=["GET", "POST"])
def perfil(id=id):
    if "usuario" in session:
        try:
            with sqlite3.connect(ruta_db) as con:
                con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute("SELECT * FROM tb_users WHERE correo=?", [id])
                row_perfil = cur.fetchone()
                rol = session["rol"]
                con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
                cur = con.cursor()
                cur.execute(
                    "SELECT * FROM tb_comentario WHERE usuario=?", [session["usuario"]])
                row_comentarios = cur.fetchall()
                return render_template(ruta_perfil, row_usuario=row_perfil, rol=rol, row_comentarios=row_comentarios, inicio=1, id=session["usuario"])
        except Error:
            print(Error)
    return "Debe iniciar sesion"


@app.route("/cart", methods=["GET", "POST"])
def cart():
    products, grand_total, quantity_total = handle_cart()

    return render_template("cart.html", products=products, grand_total=grand_total, quantity_total=quantity_total, inicio=1, rol="comprador",id=session["usuario"])


@app.route("/addToCart/<string:id_producto>", methods=["GET", "POST"])
def addToCart(id_producto=None):
    if "usuario" in session:
        cantidad = request.form.get("cantidad")
        print(cantidad)
        print(type(cantidad))
        if cantidad == "0":
            return "Seleccione un valor mayor a 0"
        carrito = session["cart"]
        carrito.append({"id": id_producto, "cantidad": cantidad})
        session["cart"] = carrito

        return redirect("/productos")
    else:
        return "Debe iniciar sesion"


@app.route("/remove_from_cart/<string:index>", methods=["GET", "POST"])
def remove_from_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    for item in session["cart"]:
        print(item["id"])
        try:
            with sqlite3.connect(ruta_db) as con:
                con.row_factory = sqlite3.Row
                cur=con.cursor()
                cur.execute("SELECT * FROM tb_productos WHERE id_producto=?", [item["id"]])
                row_producto = cur.fetchone()
                quantity = int(item['cantidad'])
                valor_ventas = quantity * row_producto["precio_unidad"]
                cur=con.cursor()
                cur.execute("UPDATE tb_productos SET unidades_vendidas=unidades_vendidas+?, valor_ventas=valor_ventas+?, total_unidades=total_unidades-? where id_producto=?",(quantity,valor_ventas,quantity,item["id"]))
                con.commit()
                cur.execute("UPDATE tb_users SET acumulado_compras=acumulado_compras+? where correo=?",(valor_ventas,session["usuario"]))
                con.commit()

                cur = con.cursor()
                cur.execute("INSERT INTO tb_ventas (producto, num_unidades, bono_descuento, descuento, total) VALUES (?,?,?,?,?)", (
                    row_producto["nombre_producto"], quantity,"no",0,valor_ventas))
                con.commit()

                


        except:
            print("Error")
            return "Error"
    session["cart"]=[]
    return render_template("compraExitosa.html",inicio=1, rol="comprador")
    
@app.route('/eliminarComentario/<string:id>', methods=["GET","POST"])
def eliminarComentario(id=None):
    try:
        with sqlite3.connect(ruta_db) as con:
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute("SELECT * FROM tb_users WHERE correo=?", [session["usuario"]])
            row_perfil = cur.fetchone()
         
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM tb_comentario WHERE usuario=?", [session["usuario"]])
            row_comentarios = cur.fetchall()
            
            cur = con.cursor()
            cur.execute("DELETE FROM tb_comentario WHERE id_comentario = ?",[int(id)])
            
            con.row_factory = sqlite3.Row  # Convierte la respuesta de la BD en un diccionario
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM tb_comentario WHERE usuario=?", [session["usuario"]])
            row_comentarios = cur.fetchall()
            return render_template(ruta_perfil, row_usuario=row_perfil, row_comentarios=row_comentarios, inicio=1, id=session["usuario"])
    except:
        print("Error")
        return "Error"




if __name__ == "__main__":
    app.run(debug=True, port=8000)
