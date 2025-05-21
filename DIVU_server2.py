from systec_opc_client import systec, systec_opc_client
from Divu_class import DIVU
from flask import Flask, render_template, request
import os
import sys
import signal
import argparse
import time
import datetime

# OPC set up
constr = "opc.tcp://localhost:4841"

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--constr', help="connection string: %s" % constr, default=constr)
parser.add_argument('-v', '--verbose', help="enable verbose mode", action="store_true")

args = parser.parse_args()

client = systec_opc_client(args.constr)
client.SetVerbose(args.verbose)
if not client.Open(): sys.exit()

divu = DIVU()
divu.init_device()

app = Flask(__name__)

def get_opc_channel_value(channel_number):
    """Get the current temperature value from the OPC server for a specific channel"""
    systec_instance = client.GetSystec()
    if not systec_instance:
        return None
    
    channel_name = f"Chan_{channel_number:02d}"
    
    try:
        channel_node = systec_instance.GetNode(channel_name)
        if channel_node:
            value = channel_node.get_value()
            return float(value) if value is not None else None
    except Exception as e:
        print(f"Error reading channel {channel_number} from OPC server: {e}")
    
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_temp = None
    selected_channel = 1  # Default to channel 1
    channel_data = None
    
    if request.method == 'POST':
        try:
            selected_temp = float(request.form.get('temperature'))
            selected_channel = int(request.form.get('channel', 1))
            
            # Set theoretical temperature using DIVU
            theoreticalR, theoreticalT = divu.set_temp(f"Chan{selected_channel}", selected_temp)
            theoreticalR = divu.temperature_to_resistance(theoreticalR)
            
            # Get actual measured temperature from OPC server
            measuredR = divu.voltage_to_resistance(get_opc_channel_value(selected_channel))
            measuredT = divu.resistance_to_temperature(measuredR)
            
            channel_data = {
                'theoretical': {
                    'R': float(theoreticalR) if theoreticalR is not None else 0.0,
                    'T': float(theoreticalT) if theoreticalT is not None else 0.0
                },
                'measured': {
                    'R': float(measuredR) if measuredR is not None else 0.0,
                    'T': float(measuredT) if measuredT is not None else 0.0
                },
                'error': {
                    'R': (float(measuredR) if measuredR is not None else 0.0) - 
                         (float(theoreticalR) if theoreticalR is not None else 0.0),
                    'T': (float(measuredT) if measuredT is not None else 0.0) - 
                         (float(theoreticalT) if theoreticalT is not None else 0.0)
                }
            }
                
        except (TypeError, ValueError) as e:
            print(f"Error processing input: {e}")
            channel_data = {
                'theoretical': {'R': 0.0, 'T': 0.0},
                'measured': {'R': 0.0, 'T': 0.0},
                'error': {'R': 0.0, 'T': 0.0}
            }
    
    return render_template(
        'divu_test2.html',
        temperatures=[-80, -45, 0, 25, 60],
        channels=range(1, 49),
        selected_temp=selected_temp,
        selected_channel=selected_channel,
        channel_data=channel_data if channel_data else {
            'theoretical': {'R': 0.0, 'T': 0.0},
            'measured': {'R': 0.0, 'T': 0.0},
            'error': {'R': 0.0, 'T': 0.0}
        }
    )

if __name__ == '__main__':
    from werkzeug.serving import is_running_from_reloader
    
    if not is_running_from_reloader:
        def shutdown_server(signal, frame):
            print("\nShutting down server...")
            client.Close()  # Close OPC connection
            os._exit(0)
        
        signal.signal(signal.SIGINT, shutdown_server)
    
    app.run(host='0.0.0.0', port=5000, debug=True)