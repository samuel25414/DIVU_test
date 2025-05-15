from flask import Flask, render_template, request
import random

app = Flask(__name__)

# Simulated data for each channel at different temperatures
def generate_simulated_data():
    temperatures = [-80, -45, -0, 25, 60]
    channels = range(1, 49)
    
    data = {}
    for temp in temperatures:
        data[temp] = {}
        for channel in channels:
            # Generate theoretical R and T values
            base_r = 1000 + channel * 10  # Varies by channel
            base_t = temp + random.uniform(-0.5, 0.5)  # Close to selected temp
            
            # Generate measured values with some variation
            measured_r = base_r * random.uniform(0.98, 1.02)
            measured_t = base_t * random.uniform(0.98, 1.02)
            
            # Calculate errors
            error_r = abs(measured_r - base_r)
            error_t = abs(measured_t - base_t)
            
            data[temp][channel] = {
                'theoretical': {'R': base_r, 'T': base_t},
                'measured': {'R': measured_r, 'T': measured_t},
                'error': {'R': error_r, 'T': error_t}
            }
    return data

simulated_data = generate_simulated_data()

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_temp = None
    selected_channel = 1  # Default to channel 1
    channel_data = None
    
    if request.method == 'POST':
        try:
            selected_temp = int(request.form.get('temperature'))
            selected_channel = int(request.form.get('channel', 1))
            
            if selected_temp in simulated_data and selected_channel in simulated_data[selected_temp]:
                channel_data = simulated_data[selected_temp][selected_channel]
        except (TypeError, ValueError):
            # Handle cases where conversion fails (None or invalid input)
            pass
    
    return render_template(
        'divu_test.html',
        temperatures=[-80, -45, -0, 25, 60],
        channels=range(1, 49),
        selected_temp=selected_temp,
        selected_channel=selected_channel,
        channel_data=channel_data
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
