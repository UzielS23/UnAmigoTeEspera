from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import mysql.connector
from mysql.connector import Error

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


@app.route('/api/refugios/<int:idRefugio>/force_delete', methods=['POST'])
def api_force_delete_refugio(idRefugio):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        # obtener ids de mascotas del refugio
        cursor.execute("SELECT idMascota FROM mascotas WHERE idRefugio = %s", (idRefugio,))
        filas = cursor.fetchall()
        mascota_ids = [r[0] for r in filas]

        # borrar apoyos que referencian directamente el refugio
        cursor.execute("DELETE FROM apoyos WHERE idRefugio = %s", (idRefugio,))

        # borrar apoyos que referencian a las mascotas de ese refugio
        if mascota_ids:
            placeholders = ','.join(['%s'] * len(mascota_ids))
            cursor.execute(f"DELETE FROM apoyos WHERE idMascota IN ({placeholders})", tuple(mascota_ids))

            # borrar adopciones relacionadas a esas mascotas
            cursor.execute(f"DELETE FROM adopciones WHERE idMascota IN ({placeholders})", tuple(mascota_ids))

            # borrar las mascotas
            cursor.execute(f"DELETE FROM mascotas WHERE idMascota IN ({placeholders})", tuple(mascota_ids))

        # finalmente borrar el refugio
        cursor.execute("DELETE FROM refugios WHERE idRefugio = %s", (idRefugio,))

        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True, 'message': 'Refugio y datos relacionados eliminados'})
    except Error as e:
        try:
            db.rollback()
        except Exception:
            pass
        try:
            cursor.close()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        try:
            cursor.close()
        except Exception:
            pass
        try:
            db.close()
        except Exception:
            pass
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


# API: listado de refugios (JSON)
@app.route('/api/refugios', methods=['GET'])
def api_list_refugios():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT idRefugio, nombre, direccion, telefono, correoElectronico, capacidad, fechaFundacion, descripcion FROM refugios ORDER BY idRefugio DESC")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(rows)
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# API: crear refugio
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
        """, (nombre, direccion, telefono or None, correo, capacidad or None, fecha or None, descripcion))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()
        return jsonify({'success': True, 'message': 'Refugio creado', 'idRefugio': new_id})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# API: actualizar refugio
@app.route('/api/refugios/<int:idRefugio>', methods=['PUT'])
def api_update_refugio(idRefugio):
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
            UPDATE refugios
            SET nombre=%s, direccion=%s, telefono=%s, correoElectronico=%s, capacidad=%s, fechaFundacion=%s, descripcion=%s
            WHERE idRefugio=%s
        """, (nombre, direccion, telefono or None, correo, capacidad or None, fecha or None, descripcion, idRefugio))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True, 'message': 'Refugio actualizado'})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# API: eliminar refugio
@app.route('/api/refugios/<int:idRefugio>', methods=['DELETE'])
def api_delete_refugio(idRefugio):
    try:
        force = request.args.get('force', '0')
        db = get_db_connection()
        cursor = db.cursor()

        if force and force.lower() in ('1', 'true'):
            # Borrar apoyos relacionados explícitamente antes de borrar el refugio.
            # Además, borrar apoyos asociados a mascotas del refugio y las mascotas y adopciones relacionadas.
            try:
                # obtener ids de mascotas del refugio
                cursor.execute("SELECT idMascota FROM mascotas WHERE idRefugio = %s", (idRefugio,))
                filas = cursor.fetchall()
                mascota_ids = [r[0] for r in filas]

                # borrar apoyos que referencian directamente el refugio
                cursor.execute("DELETE FROM apoyos WHERE idRefugio = %s", (idRefugio,))

                # borrar apoyos que referencian a las mascotas de ese refugio
                if mascota_ids:
                    placeholders = ','.join(['%s'] * len(mascota_ids))
                    cursor.execute(f"DELETE FROM apoyos WHERE idMascota IN ({placeholders})", tuple(mascota_ids))

                    # borrar adopciones relacionadas a esas mascotas
                    cursor.execute(f"DELETE FROM adopciones WHERE idMascota IN ({placeholders})", tuple(mascota_ids))

                    # borrar las mascotas
                    cursor.execute(f"DELETE FROM mascotas WHERE idMascota IN ({placeholders})", tuple(mascota_ids))

                # finalmente borrar el refugio
                cursor.execute("DELETE FROM refugios WHERE idRefugio = %s", (idRefugio,))

                db.commit()
                cursor.close()
                db.close()
                return jsonify({'success': True, 'message': 'Refugio y datos relacionados eliminados'})
            except Exception as ex:
                db.rollback()
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    db.close()
                except Exception:
                    pass
                return jsonify({'success': False, 'message': str(ex)}), 500

        # Intento de borrado normal
        cursor.execute("DELETE FROM refugios WHERE idRefugio = %s", (idRefugio,))
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'success': True, 'message': 'Refugio eliminado'})
    except Error as e:
        # Código de MySQL para foreign key constraint failure es 1451
        try:
            err_no = getattr(e, 'errno', None)
        except Exception:
            err_no = None
        if err_no == 1451:
                # Indicar al frontend que existen dependencias. Calculamos recuentos para mostrar detalle.
                try:
                    # contar apoyos directamente vinculados por idRefugio
                    cursor.execute("SELECT COUNT(*) FROM apoyos WHERE idRefugio = %s", (idRefugio,))
                    apoyos_directos = cursor.fetchone()[0]
                    # contar mascotas del refugio
                    cursor.execute("SELECT idMascota FROM mascotas WHERE idRefugio = %s", (idRefugio,))
                    filas = cursor.fetchall()
                    mascota_ids = [r[0] for r in filas]
                    mascotas_count = len(mascota_ids)
                    apoyos_por_mascota = 0
                    if mascota_ids:
                        placeholders = ','.join(['%s'] * len(mascota_ids))
                        cursor.execute(f"SELECT COUNT(*) FROM apoyos WHERE idMascota IN ({placeholders})", tuple(mascota_ids))
                        apoyos_por_mascota = cursor.fetchone()[0]
                    total_apoyos = apoyos_directos + apoyos_por_mascota
                except Exception:
                    total_apoyos = None
                    mascotas_count = None
                try:
                    cursor.close()
                except Exception:
                    pass
                try:
                    db.close()
                except Exception:
                    pass
                info = {'success': False, 'code': 'fk_dependency', 'message': 'Existen dependencias relacionadas con este refugio.', 'dependentCounts': {'apoyos': total_apoyos, 'mascotas': mascotas_count}}
                return jsonify(info), 409
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/notificaciones")
def notificaciones():
    return render_template("notificaciones.html")

@app.route("/partials/<name>")
def partials(name):
    return render_template(f"{name}.html")

if __name__ == '__main__':
    # Cambiado para acceder desde otros dispositivos en la misma red
    app.run(host='0.0.0.0', port=5000, debug=True)