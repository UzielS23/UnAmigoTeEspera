from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

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

@app.route("/apoyos")
def apoyos():
    return render_template("apoyos.html")

@app.route("/mascotas")
def mascotas():
    return render_template("mascotas.html")

@app.route("/refugios")
def refugios():
    return render_template("refugios.html")

@app.route("/notificaciones")
def notificaciones():
    return render_template("notificaciones.html")

@app.route("/partials/<name>")
def partials(name):
    return render_template(f"{name}.html")

if __name__ == '__main__':
    # Cambiado para acceder desde otros dispositivos en la misma red
    app.run(host='0.0.0.0', port=5000, debug=True)
