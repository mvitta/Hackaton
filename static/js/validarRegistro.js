const form = document.getElementById("formulario");

const errorCedula = document.getElementById("msgCedula");
const errorNombre = document.getElementById("msgNombre");
const errorApellido = document.getElementById("msgApellido");
const errorCorreo = document.getElementById("msgCorreo");
const errorCiudad = document.getElementById("msgCiudad");
const errorNombreUsuario = document.getElementById("msgNombreUsuario");
const errorContra1 = document.getElementById("msgPass1");
const errorContra2 = document.getElementById("msgPass2");


function validarCedula(valor) {
    if (valor.match(/^[0-9]+$/)) {
        return true;
    } else {
        return false;
    }
}

function validarNombre(valor) {
    if (valor.match(/^[A-Za-z]+$/)) {
        return true;
    }
    else {
        return false;
    }
}

function validarCiudad(valor) {
    if (valor.match(/^[A-Za-z]+$/)) {
        return true;
    }
    else {
        return false;
    }
}

function validarApellido(valor) {
    if (valor.match(/^[A-Za-z]+$/)) {
        return true;
    }
    else {
        return false;
    }
}

function validarCorreo(valor) {
    if (valor.match(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/)) {
        return true;
    }
    else {
        return false;
    }
}

function validarUsuario(valor) {
    if (valor.match(/[^A-Za-z0-9]+/)) {
        return true;
    }
    else {
        return false;
    }
}


function validarContra1(valor) {
    if (valor.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^\W_]{8,}$/)) {
        return true;
    }
    else {
        return false;
    }
}

function validarContra2(valor) {
    if (valor.match(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^\W_]{8,}$/)) {
        return true;
    }
    else {
        return false;
    }
}

form.addEventListener('submit', (e) => {

    let estado = "";
    // datos
    let datos = document.getElementsByClassName("form-control");
    let sexo = document.getElementsByName("flexRadioDefault")

    let cedula = datos[0].value;
    let nombre = datos[1].value;
    let apellido = datos[2].value;
    let correo = datos[3].value;
    let fechaNacimiento = datos[4].value;
    let direccion = datos[5].value;
    let ciudad = datos[6].value;
    let nombreUsuario = datos[7].value;
    let contra1 = datos[8].value;
    let contra2 = datos[9].value;

    valorSexo = "";
    for (let i = 0; i < sexo.length; i++) {
        const element = sexo[i];
        if (element.checked) {
            valorSexo = element.value
        }
    }
    console.log(cedula, nombre, apellido, correo, fechaNacimiento, direccion, ciudad, nombreUsuario, contra1, contra2, valorSexo)
    // reinicio de errores
    errorCedula.innerHTML = "";
    errorNombre.innerHTML = "";
    errorApellido.innerHTML = "";
    errorCorreo.innerHTML = "";
    errorContra1.innerHTML = "";
    errorContra2.innerHTML = "";
    errorCiudad.innerHTML = "";
    errorNombreUsuario.innerHTML = "";
    // validaciones

    if (!validarCedula(cedula)) {
        errorCedula.innerHTML = "La cedula no es valida";
    }
    else {
        estado += "OK";
    }

    if (!validarNombre(nombre)) {
        errorNombre.innerHTML = "El nombre no es valido";
    }
    else {
        estado += "OK";
    }

    if (!validarApellido(apellido)) {
        errorApellido.innerHTML = "El apellido no es valido";
    }
    else {
        estado += "OK";
    }

    if (!validarCorreo(correo)) {
        errorCorreo.innerHTML = "El Correo no es valido";
    }
    else {
        estado += "OK";
    }

    if (!validarCiudad(ciudad)) {
        errorCiudad.innerHTML = "la ciudad no es valida";
    }
    else {
        estado += "OK";
    }

    if (!validarUsuario(nombreUsuario)) {
        errorNombreUsuario.innerHTML = "el nombre de usuario no es valido";
    }
    else {
        estado += "OK";
    }

    if (!validarContra1(contra1)) {
        errorContra1.innerHTML = "La Contraseña no es valida";
    }
    else {
        estado += "OK";
    }

    if (estado == "OKOKOKOKOK") {
        if (contra1 == contra2) {
            estado += "OK";
        }
        else {
            errorContra2.innerHTML = "Las Contrasena no coinciden"
        }
    }

    if (estado == "OKOKOKOKOKOKOKOK") {

    } else {
        e.preventDefault();
    }

});