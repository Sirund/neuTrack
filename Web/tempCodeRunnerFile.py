from flask import Flask, render_template
from subprocess import Popen, PIPE, STDOUT
import folium

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gps')
def gps():
    try:
        # Start GPS_print.py
        print_process = Popen(['python', 'GPS_print.py'], stdout=PIPE, stderr=STDOUT, text=True)

        # Start GPS_send.py
        send_process = Popen(['python', 'GPS_send.py'], stdout=PIPE, stderr=STDOUT, text=True)

        # Wait for processes to complete
        print_output, _ = print_process.communicate()
        send_output, _ = send_process.communicate()

        print("GPS Print Output:", print_output)
        print("GPS Send Output:", send_output)

        # Read current location from the file
        with open('location.txt', 'r') as f:
            location_data = f.read().split(',')

        latitude, longitude = map(float, location_data)

        # Create a map using folium
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        folium.Marker([latitude, longitude], popup='Your Location').add_to(m)

        # Save the map as an HTML file
        m.save('templates/map.html')

    except Exception as e:
        print(f"An error occurred: {e}")

    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
