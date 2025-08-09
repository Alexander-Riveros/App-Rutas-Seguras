from flask import Flask, render_template, request, redirect, session, jsonify
import firebase_admin
from firebase_admin import credentials, auth, db
import base64
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'  # Cambia esto por una clave secreta real

# =======================
# Inicializar Firebase
# =======================
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://app-rutas-seguras-default-rtdb.firebaseio.com/'
})

# =======================
# Carpetas y referencias
# =======================
UPLOAD_FOLDER = 'static/fotos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

usuarios_ref = db.reference('/usuarios')
rutas_ref = db.reference('/rutas')  # Referencia para rutas

# =======================
# Rutas HTML (Frontend)
# =======================
@app.route('/')
def index():
    return render_template("layout.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/gps')
def gps():
    return render_template("gps.html")

@app.route('/camara')
def camara():
    return render_template("camara.html")

@app.route("/rutas")
def ver_rutas():
    return render_template("rutas.html")

@app.route('/perfil.html')
def perfil():
    if 'nombre' in session and 'correo' in session:
        return render_template('perfil.html', nombre=session['nombre'], correo=session['correo'])
    else:
        return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/home')

# =======================
# Registro y login
# =======================
@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    data = request.json
    nombre = data['nombre']
    correo = data['correo']
    clave = data['clave']

    try:
        user = auth.create_user(email=correo, password=clave, display_name=nombre)
        usuarios_ref.child(user.uid).set({
            "nombre": nombre,
            "correo": correo
        })
        return jsonify({"mensaje": f"Usuario {nombre} registrado con éxito."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login_usuario():
    data = request.json
    correo = data['correo']

    try:
        user = auth.get_user_by_email(correo)
        user_data = usuarios_ref.child(user.uid).get()
        if user_data:
            session['nombre'] = user_data.get('nombre', '')
            session['correo'] = user_data.get('correo', '')
            return jsonify({"mensaje": f"Bienvenido {user.display_name}"}), 200
        else:
            return jsonify({"error": "Datos de usuario no encontrados en base de datos"}), 404
    except:
        return jsonify({"error": "Usuario no encontrado"}), 404

# =======================
# CRUD genérico de datos
# =======================
@app.route('/crear', methods=['POST'])
def crear():
    data = request.json
    ref = db.reference('datos')
    nuevo = ref.push(data)
    return jsonify({"id": nuevo.key}), 200

@app.route('/leer', methods=['GET'])
def leer():
    ref = db.reference('datos')
    datos = ref.get()
    return jsonify(datos or {}), 200

@app.route('/eliminar/<id>', methods=['DELETE'])
def eliminar(id):
    ref = db.reference(f'datos/{id}')
    ref.delete()
    return jsonify({"mensaje": "Eliminado"}), 200

# =======================
# CRUD Usuarios
# =======================
@app.route('/leer_usuarios', methods=['GET'])
def leer_usuarios():
    return jsonify(usuarios_ref.get() or {}), 200

@app.route('/eliminar_usuario/<id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuarios_ref.child(id).delete()
    return jsonify({'mensaje': 'Usuario eliminado'}), 200

# =======================
# Guardar foto desde cámara
# =======================
@app.route('/guardar_foto', methods=['POST'])
def guardar_foto():
    datos = request.get_json()
    imagen_base64 = datos.get('imagen', '')

    if not imagen_base64.startswith('data:image'):
        return jsonify({"error": "Formato de imagen no válido"}), 400

    base64_data = imagen_base64.split(',')[1]
    imagen_binaria = base64.b64decode(base64_data)

    nombre_archivo = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    ruta_archivo = os.path.join(UPLOAD_FOLDER, nombre_archivo)

    with open(ruta_archivo, 'wb') as f:
        f.write(imagen_binaria)

    return jsonify({"mensaje": "Foto guardada correctamente", "archivo": nombre_archivo}), 200

# =======================
# Iniciar servidor
# =======================
if __name__ == '__main__':
    app.run(debug=True)
