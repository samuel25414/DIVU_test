from Divu_class import DIVU
from flask import Flask, render_template, request

divu = DIVU()
divu.init_device()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_temp = None
    selected_channel = 1  # Default to channel 1
    channel_data = None
    
    if request.method == 'POST':
        try:
            selected_temp = int(request.form.get('temperature'))
            selected_channel = int(request.form.get('channel', 1))
            ss_chann = "Chan" + str(selected_channel)
            
            # Get ACTUAL measurements from DIVU device
            actualR, actualT = divu.set_temp(ss_chann, selected_temp)
            
            # Replace simulated data with real measurements
            channel_data = {
                'theoretical': {'R': 10000, 'T': selected_temp},  # No theoretical data
                'measured': {'R': actualR, 'T': actualT},
                'error': {'R': None, 'T': None}  # Can compute later if needed
            }
            
        except (TypeError, ValueError) as e:
            print(f"Error processing input: {e}")
    
    return render_template(
        'divu_test.html',
        temperatures=[-80, -45, -0, 25, 60],
        channels=range(1, 49),
        selected_temp=selected_temp,
        selected_channel=selected_channel,
        channel_data=channel_data  # Now contains real data
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
