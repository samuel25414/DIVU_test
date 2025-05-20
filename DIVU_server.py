from systec_opc_client import systec, systec_opc_client
from Divu_class import DIVU
from flask import Flask, render_template, request

#--------------------------------OPC set up ------------------------------------------------------
import os
import sys
import signal
import argparse
import time
import datetime

constr="opc.tcp://localhost:4841"

parser=argparse.ArgumentParser()
parser.add_argument('-s','--constr',help="connection string: %s" % constr, default=constr)
parser.add_argument('-v','--verbose',help="enable verbose mode", action="store_true")

args=parser.parse_args()

client=systec_opc_client(args.constr)
client.SetVerbose(args.verbose)
if not client.Open(): sys.exit()

cont = True
def signal_handler(signal, frame):
    print("You pressed ctrl+C")
    global cont
    cont = False
    return

signal.signal(signal.SIGINT, signal_handler)

#-----------------------------------------------------------------------------------------------

divu = DIVU()
divu.init_device()

app = Flask(__name__)

def get_opc_channel_value(channel_number):
    """Get the current temperature value from the OPC server for a specific channel"""
    systec_instance = client.GetSystec()
    if not systec_instance:
        return None
    
    # Format channel number to match node names (e.g., "Chan_01")
    channel_name = f"Chan_{channel_number:02d}"
    
    try:
        channel_node = systec_instance.GetNode(channel_name)
        if channel_node:
            return channel_node.get_value()
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
            selected_temp = int(request.form.get('temperature'))
            selected_channel = int(request.form.get('channel', 1))
            
            # Set theoretical temperature using DIVU
            theoreticalR, theoreticalT = divu.set_temp(f"Chan{selected_channel}", selected_temp)
            theoreticalR = divu.temperature_to_resistance(theoreticalR)
            
            # Get actual measured temperature from OPC server
            measuredT = get_opc_channel_value(selected_channel)
            measuredR = divu.temperature_to_resistance(measuredT)
            if measuredT is not None:
                channel_data = {
                    'theoretical': {
                        'R': theoreticalR if theoreticalR is not None else 0,
                        'T': theoreticalT if theoreticalT is not None else 0
                    },
                    'measured': {
                        'R': measuredR if measuredR is not None else 0,
                        'T': measuredT if measuredT is not None else 0
                    },
                    'error': {
                        'R': (measuredR if measuredR is not None else 0) - (theoreticalR if theoreticalR is not None else 0),
                        'T': (measuredT if measuredT is not None else 0) - (theoreticalT if theoreticalT is not None else 0)
                    }
                }
            else:
                print(f"Could not read measured temperature for channel {selected_channel}")
                # Provide default data even if measurement fails
                channel_data = {
                    'theoretical': {
                        'R': theoreticalR if theoreticalR is not None else 0,
                        'T': theoreticalT if theoreticalT is not None else 0
                    },
                    'measured': {
                        'R': 0,
                        'T': 0
                    },
                    'error': {
                        'R': 0 - (theoreticalR if theoreticalR is not None else 0),
                        'T': 0 - (theoreticalT if theoreticalT is not None else 0)
                    }
                }
                
        except (TypeError, ValueError) as e:
            print(f"Error processing input: {e}")
            # Provide default data on error
            channel_data = {
                'theoretical': {'R': 0, 'T': 0},
                'measured': {'R': 0, 'T': 0},
                'error': {'R': 0, 'T': 0}
            }
    
    return render_template(
        'divu_test.html',
        temperatures=[-80, -45, 0, 25, 60],
        channels=range(1, 49),
        selected_temp=selected_temp,
        selected_channel=selected_channel,
        channel_data=channel_data if channel_data else {
            'theoretical': {'R': 0, 'T': 0},
            'measured': {'R': 0, 'T': 0},
            'error': {'R': 0, 'T': 0}
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)