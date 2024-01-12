from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/path')
def path():
    return render_template('path.html')

@app.route('/shortest')
def shortest():
    return render_template('shortest.html')

@app.route('/gps')
def gps():
    gps_data = {"latitude": 37.7749, "longitude": -122.4194}

    return render_template('gps.html', gps_data=gps_data)

if __name__ == '__main__':
    app.run(debug=True)
