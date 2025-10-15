from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import scrypt

app = Flask(__name__)

app.secret_key = 'super_clave_segura_12345'
# 🔹 Conexión con la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # <-- cambia si usas otro usuario
        password="",          # <-- agrega tu contraseña si tienes
        database="refugiomascotas"
    )

from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/offline')
def offline():
    return render_template('offline.html')

@app.route('/dashboard-graficas')

def dashboard_graficas():
    return render_template('dashboardgraficas.html')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')

@app.route("/padrinos")
def padrinos():
    return render_template("padrinos.html")


@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    try:
        correo = request.form['email']
        contrasena = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Verificar si el correo ya existe
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': '❌ El correo ya está registrado.'}), 400

        # Encriptar la contraseña usando scrypt
        hashed_password = scrypt.hash(contrasena)

        # Insertar nuevo usuario
        cursor.execute("""
            INSERT INTO usuarios (correo, contrasena)
            VALUES (%s, %s)
        """, (correo, hashed_password))
        db.commit()
        new_id = cursor.lastrowid

        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': '✅ Usuario registrado correctamente.', 'idUsuario': new_id})

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500


@app.route('/login_usuario', methods=['POST'])
def login_usuario():
    try:
        correo = request.form['email']
        contrasena = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT idUsuario, correo, contrasena FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()

        cursor.close()
        db.close()

        if not usuario:
            return jsonify({'success': False, 'message': '❌ Usuario no encontrado.'}), 404

        if not scrypt.verify(contrasena, usuario['contrasena']):
            return jsonify({'success': False, 'message': '❌ Contraseña incorrecta.'}), 401

        # 🔹 Guardar sesión
        session['usuario_id'] = usuario['idUsuario']
        session['usuario_correo'] = usuario['correo']

        return jsonify({
            'success': True,
            'message': '✅ Inicio de sesión exitoso.',
            'idUsuario': usuario['idUsuario'],
            'correo': usuario['correo']
        })

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500
##### APOYOS

@app.route('/apoyos')
def apoyos():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
        SELECT a.idApoyo, a.idMascota, a.idPadrino, a.idRefugio,
               m.nombre AS mascota, p.nombrePadrino AS padrino,
               r.nombre AS refugio, a.monto, a.causa, a.fechaApoyo
        FROM apoyos a
        LEFT JOIN mascotas m ON a.idMascota = m.idMascota
        LEFT JOIN padrinos p ON a.idPadrino = p.idPadrino
        LEFT JOIN refugios r ON a.idRefugio = r.idRefugio
        ORDER BY a.idApoyo DESC
        """)

        apoyos = cursor.fetchall()

        cursor.execute("SELECT idMascota, nombre FROM mascotas")
        mascotas = cursor.fetchall()

        cursor.execute("SELECT idPadrino, nombrePadrino FROM padrinos")
        padrinos = cursor.fetchall()

        cursor.execute("SELECT idRefugio, nombre FROM refugios")
        refugios = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template('apoyos.html', apoyos=apoyos, mascotas=mascotas, padrinos=padrinos, refugios=refugios)

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

@app.route('/registrar_apoyo', methods=['POST'])
def registrar_apoyo():
    try:
        idMascota = request.form['idMascota']
        idPadrino = request.form['idPadrino']
        idRefugio = request.form['idRefugio']
        monto = request.form['monto']
        causa = request.form['causa']
        fechaApoyo = request.form['fechaApoyo']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO apoyos (idMascota, idPadrino, idRefugio, monto, causa, fechaApoyo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (idMascota, idPadrino, idRefugio, monto, causa, fechaApoyo))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': 'Apoyo registrado ✅', 'idApoyo': new_id})

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

@app.route('/editar_apoyo/<int:idApoyo>', methods=['POST'])
def editar_apoyo(idApoyo):
    try:
        idMascota = request.form['idMascota']
        idPadrino = request.form['idPadrino']
        idRefugio = request.form['idRefugio']
        monto = request.form['monto']
        causa = request.form['causa']
        fechaApoyo = request.form['fechaApoyo']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE apoyos
            SET idMascota=%s, idPadrino=%s, idRefugio=%s, monto=%s, causa=%s, fechaApoyo=%s
            WHERE idApoyo=%s
        """, (idMascota, idPadrino, idRefugio, monto, causa, fechaApoyo, idApoyo))
        db.commit()
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': 'Apoyo actualizado ✏️'})

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

@app.route('/eliminar_apoyo/<int:idApoyo>', methods=['POST'])
def eliminar_apoyo(idApoyo):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM apoyos WHERE idApoyo = %s", (idApoyo,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True, 'message': 'Apoyo eliminado 🗑️'})

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500
    
@app.route('/grafica_refugios')
def grafica_refugios():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT r.nombre AS refugio, SUM(a.monto) AS total
            FROM apoyos a
            JOIN refugios r ON a.idRefugio = r.idRefugio
            GROUP BY r.idRefugio, r.nombre
            ORDER BY total DESC
        """)
        datos = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(datos)

    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    

@app.route('/grafica_tiempo')
def grafica_tiempo():
    try:
        db = get_db_connection()  # ✅ conexión correcta
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT DATE_FORMAT(fechaApoyo, '%Y-%m') AS mes, SUM(monto) AS total
            FROM apoyos
            GROUP BY mes
            ORDER BY mes
        """)
        data = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(data)

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500


@app.route('/lista_apoyos')
def lista_apoyos():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
        SELECT a.idApoyo, a.idMascota, a.idPadrino, a.idRefugio,
               m.nombre AS mascota, p.nombrePadrino AS padrino,
               r.nombre AS refugio, a.monto, a.causa, a.fechaApoyo
        FROM apoyos a
        LEFT JOIN mascotas m ON a.idMascota = m.idMascota
        LEFT JOIN padrinos p ON a.idPadrino = p.idPadrino
        LEFT JOIN refugios r ON a.idRefugio = r.idRefugio
        ORDER BY a.idApoyo DESC
        """)
        apoyos = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('_lista_apoyos.html', apoyos=apoyos)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/partials/apoyos')
def partial_apoyos():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
        SELECT a.idApoyo, a.idMascota, a.idPadrino, a.idRefugio,
               m.nombre AS mascota, p.nombrePadrino AS padrino,
               r.nombre AS refugio, a.monto, a.causa, a.fechaApoyo
        FROM apoyos a
        LEFT JOIN mascotas m ON a.idMascota = m.idMascota
        LEFT JOIN padrinos p ON a.idPadrino = p.idPadrino
        LEFT JOIN refugios r ON a.idRefugio = r.idRefugio
        ORDER BY a.idApoyo DESC
        """)
        apoyos = cursor.fetchall()

        cursor.execute("SELECT idMascota, nombre FROM mascotas")
        mascotas = cursor.fetchall()

        cursor.execute("SELECT idPadrino, nombrePadrino FROM padrinos")
        padrinos = cursor.fetchall()

        cursor.execute("SELECT idRefugio, nombre FROM refugios")
        refugios = cursor.fetchall()

        cursor.close()
        db.close()

        # Devuelve TODO el HTML completo de apoyos.html
        return render_template('apoyos.html', apoyos=apoyos, mascotas=mascotas, padrinos=padrinos, refugios=refugios)

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

####### MASCOTAS
@app.route("/mascotas")
def mascotas():
    return render_template("mascotas.html")

@app.route("/refugios")
def refugios():
    return render_template("refugios.html")


### API REST para Refugios
@app.route('/api/refugios', methods=['GET'])
def api_list_refugios():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM refugios ORDER BY idRefugio DESC")
        refugios = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(refugios)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/refugios/<int:id>', methods=['GET'])
def api_get_refugio(id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT * FROM refugios WHERE idRefugio = %s', (id,))
        r = cursor.fetchone()
        cursor.close()
        db.close()
        if not r:
            return jsonify({'success': False, 'message': 'Refugio no encontrado'}), 404
        return jsonify(r)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/refugios', methods=['POST'])
def api_create_refugio():
    try:
        data = request.get_json() or {}
        nombre = data.get('nombre')
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        correo = data.get('correoElectronico')
        capacidad = data.get('capacidad')
        fecha = data.get('fechaFundacion')
        descripcion = data.get('descripcion')

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO refugios (nombre, direccion, telefono, correoElectronico, capacidad, fechaFundacion, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, direccion, telefono, correo, capacidad, fecha, descripcion))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return jsonify({'success': True, 'message': 'Refugio creado', 'idRefugio': new_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/refugios/<int:id>', methods=['PUT'])
def api_update_refugio(id):
    try:
        data = request.get_json() or {}
        nombre = data.get('nombre')
        direccion = data.get('direccion')
        telefono = data.get('telefono')
        correo = data.get('correoElectronico')
        capacidad = data.get('capacidad')
        fecha = data.get('fechaFundacion')
        descripcion = data.get('descripcion')

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE refugios SET nombre=%s, direccion=%s, telefono=%s, correoElectronico=%s, capacidad=%s, fechaFundacion=%s, descripcion=%s
            WHERE idRefugio=%s
        """, (nombre, direccion, telefono, correo, capacidad, fecha, descripcion, id))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True, 'message': 'Refugio actualizado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/refugios/<int:id>', methods=['DELETE'])
def api_delete_refugio(id):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # intentar eliminar
        try:
            cursor.execute('DELETE FROM refugios WHERE idRefugio = %s', (id,))
            db.commit()
            affected = cursor.rowcount
            cursor.close()
            db.close()
            if affected == 0:
                return jsonify({'success': False, 'message': 'Refugio no encontrado'}), 404
            return jsonify({'success': True, 'message': 'Refugio eliminado'})
        except mysql.connector.Error as err:
            # código 1451: constraint fails (foreign key)
            if getattr(err, 'errno', None) == 1451:
                # contar dependencias para informar al cliente
                cursor_dep = db.cursor()
                cursor_dep.execute('SELECT COUNT(*) FROM apoyos WHERE idRefugio = %s', (id,))
                apoyos_count = cursor_dep.fetchone()[0]
                cursor_dep.execute('SELECT COUNT(*) FROM mascotas WHERE idRefugio = %s', (id,))
                mascotas_count = cursor_dep.fetchone()[0]
                cursor_dep.close()
                db.close()
                return jsonify({'success': False, 'message': 'Existen dependencias relacionadas', 'code': 'fk_dependency', 'dependentCounts': {'apoyos': apoyos_count, 'mascotas': mascotas_count}}), 409
            else:
                cursor.close()
                db.close()
                return jsonify({'success': False, 'message': str(err)}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/refugios/<int:id>/force_delete', methods=['POST'])
def api_force_delete_refugio(id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Contar dependencias para el mensaje de retorno
        cursor.execute('SELECT COUNT(*) FROM apoyos WHERE idRefugio = %s', (id,))
        apoyos_count = cursor.fetchone()[0]
        cursor.execute('SELECT idMascota FROM mascotas WHERE idRefugio = %s', (id,))
        mascotas_rows = cursor.fetchall()
        mascotas_ids = [r[0] for r in mascotas_rows]
        mascotas_count = len(mascotas_ids)

        # Empezar transacción manual
        try:
            # Eliminar apoyos directamente ligados al refugio
            cursor.execute('DELETE FROM apoyos WHERE idRefugio = %s', (id,))

            # Si existen mascotas del refugio, eliminar apoyos relacionados con esas mascotas y luego las mascotas
            if mascotas_ids:
                format_ids = ','.join(['%s'] * len(mascotas_ids))
                # eliminar apoyos que referencien a esas mascotas
                cursor.execute(f"DELETE FROM apoyos WHERE idMascota IN ({format_ids})", tuple(mascotas_ids))
                # eliminar adopciones relacionadas con esas mascotas
                cursor.execute(f"DELETE FROM adopciones WHERE idMascota IN ({format_ids})", tuple(mascotas_ids))
                # eliminar mascotas
                cursor.execute(f"DELETE FROM mascotas WHERE idRefugio = %s", (id,))

            # Finalmente eliminar el refugio
            cursor.execute('DELETE FROM refugios WHERE idRefugio = %s', (id,))
            db.commit()
            cursor.close()
            db.close()
            return jsonify({'success': True, 'message': 'Refugio y dependencias eliminadas', 'dependentCounts': {'apoyos': apoyos_count, 'mascotas': mascotas_count}})
        except Exception as e:
            db.rollback()
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': f'Error al eliminar en cascada: {str(e)}'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/notificaciones")
def notificaciones():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT n.id, n.usuario_id, n.tipo_accion, n.descripcion, n.fecha,
                   u.correo AS usuario_correo
            FROM notificaciones n
            LEFT JOIN usuarios u ON n.usuario_id = u.idUsuario
            ORDER BY n.fecha DESC
        """)
        notificaciones = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template("notificaciones.html", notificaciones=notificaciones)

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al obtener notificaciones: {str(e)}'}), 500


@app.route('/listar_notificaciones')
@login_required
def listar_notificaciones():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Consulta todas las notificaciones ordenadas por fecha descendente
        cursor.execute("""
            SELECT n.id, n.usuario_id, n.tipo_accion, n.descripcion, n.fecha,
                   u.correo AS usuario_correo
            FROM notificaciones n
            LEFT JOIN usuarios u ON n.usuario_id = u.idUsuario
            ORDER BY n.fecha DESC
        """)
        notificaciones = cursor.fetchall()

        cursor.close()
        db.close()

        # Renderiza el template pasando las notificaciones
        return render_template("notificaciones.html", notificaciones=notificaciones)

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al obtener notificaciones: {str(e)}'}), 500


@app.route("/partials/<name>")
def partials(name):
    return render_template(f"{name}.html")

#MASCOTAS#

# API: listado de mascotas (JSON)
@app.route('/api/mascotas', methods=['GET'])
def api_list_mascotas():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.*, r.nombre as nombreRefugio 
            FROM mascotas m 
            LEFT JOIN refugios r ON m.idRefugio = r.idRefugio 
            ORDER BY m.idMascota DESC
        """)
        mascotas = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(mascotas)
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API: crear mascota
@app.route('/api/mascotas', methods=['POST'])
def api_create_mascota():
    try:
        data = request.get_json() or {}
        
        nombre = data.get('nombre')
        animal = data.get('animal')
        sexo = data.get('sexo')
        raza = data.get('raza')
        peso = data.get('peso')
        condiciones = data.get('condiciones')
        edad = data.get('edad')
        fechaIngreso = data.get('fechaIngreso')
        idRefugio = data.get('idRefugio')
        estado = data.get('estado')

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO mascotas (nombre, animal, sexo, raza, peso, condiciones, edad, fechaIngreso, idRefugio, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, animal, sexo, raza or None, peso, condiciones or None, edad or None, fechaIngreso, idRefugio, estado))
        
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()

        return jsonify({'success': True, 'message': 'Mascota registrada ✅', 'idMascota': new_id})

    except Error as e:
        return jsonify({'success': False, 'message': f'Error de base de datos: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error del servidor: {str(e)}'}), 500

# API: obtener mascota por ID
@app.route('/api/mascotas/<int:idMascota>', methods=['GET'])
def api_get_mascota(idMascota):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.*, r.nombre as nombreRefugio 
            FROM mascotas m 
            LEFT JOIN refugios r ON m.idRefugio = r.idRefugio 
            WHERE m.idMascota = %s
        """, (idMascota,))
        mascota = cursor.fetchone()
        cursor.close()
        db.close()
        
        if mascota:
            return jsonify(mascota)
        else:
            return jsonify({'success': False, 'message': 'Mascota no encontrada'}), 404
            
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API: actualizar mascota
@app.route('/api/mascotas/<int:idMascota>', methods=['PUT'])
def api_update_mascota(idMascota):
    try:
        data = request.get_json() or {}
        
        nombre = data.get('nombre')
        animal = data.get('animal')
        sexo = data.get('sexo')
        raza = data.get('raza')
        peso = data.get('peso')
        condiciones = data.get('condiciones')
        edad = data.get('edad')
        fechaIngreso = data.get('fechaIngreso')
        idRefugio = data.get('idRefugio')
        estado = data.get('estado')

        # Validar campos requeridos
        if not all([nombre, animal, sexo, peso, fechaIngreso, idRefugio, estado]):
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400

        db = get_db_connection()
        cursor = db.cursor()

        # Verificar si el refugio existe
        cursor.execute('SELECT idRefugio FROM refugios WHERE idRefugio = %s', (idRefugio,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({'success': False, 'message': 'Refugio no encontrado'}), 404

        # Actualizar la mascota
        cursor.execute("""
            UPDATE mascotas 
            SET nombre=%s, animal=%s, sexo=%s, raza=%s, peso=%s, 
                condiciones=%s, edad=%s, fechaIngreso=%s, idRefugio=%s, estado=%s
            WHERE idMascota=%s
        """, (nombre, animal, sexo, raza or None, peso, condiciones or None, 
              edad or None, fechaIngreso, idRefugio, estado, idMascota))
        
        db.commit()
        affected = cursor.rowcount
        cursor.close()
        db.close()

        if affected > 0:
            return jsonify({'success': True, 'message': 'Mascota actualizada ✏️'})
        else:
            return jsonify({'success': False, 'message': 'Mascota no encontrada'}), 404

    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# API: eliminar mascota
@app.route('/api/mascotas/<int:idMascota>', methods=['DELETE'])
def api_delete_mascota(idMascota):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Verificar dependencias en apoyos y adopciones
        cursor.execute("SELECT COUNT(*) FROM apoyos WHERE idMascota = %s", (idMascota,))
        apoyos_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM adopciones WHERE idMascota = %s", (idMascota,))
        adopciones_count = cursor.fetchone()[0]
        
        if apoyos_count > 0 or adopciones_count > 0:
            cursor.close()
            db.close()
            return jsonify({
                'success': False,
                'code': 'fk_dependency',
                'message': 'No se puede eliminar la mascota debido a registros relacionados.',
                'dependentCounts': {'apoyos': apoyos_count, 'adopciones': adopciones_count}
            }), 409

        # Eliminar la mascota
        cursor.execute("DELETE FROM mascotas WHERE idMascota = %s", (idMascota,))
        db.commit()
        affected = cursor.rowcount
        cursor.close()
        db.close()
        
        if affected > 0:
            return jsonify({'success': True, 'message': 'Mascota eliminada 🗑️'})
        else:
            return jsonify({'success': False, 'message': 'Mascota no encontrada'}), 404
            
    except Error as e:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        cursor.close()
        db.close()
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    # Cambiado para acceder desde otros dispositivos en la misma red
    app.run(host='0.0.0.0', port=5000, debug=True)
