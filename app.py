from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')


@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')



if __name__ == '__main__':
    app.run(debug=True)
