import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
import subprocess
from comms.mqtt import interface as mqtt_interface

def mqtt_callback(client, userdata, message):
    payload = message.payload
    decoded_payload = ""
    try:
        decoded_payload = payload.decode("utf-8")
    except:
        pass

    parsed_topic = message.topic.split('/')[-1]

    if parsed_topic == "pulse":
        mqtt_manager.register_pulse(decoded_payload)

# Button callbacks
def wallu_callback():
	print("Pressed WALL-U Button")
	global local
	global process
	global gui_status
	global main_status
	global wallu_status
	global process_name
	global python_string
	if gui_status == 0 and main_status == 0:
		if local.get() == 1:
			process = subprocess.Popen([python_string, './main_module.py', '--local'])
			print("Starting local subprocess")
		else:
			process = subprocess.Popen([python_string, './main_module.py'])
		gui_status = 1
		process_name = "WALL-U Main Controller"

def cannon_callback():
	global local
	global process
	global gui_status
	global main_status
	global cannon_status
	global process_name
	if gui_status == 0 and cannon_status == 0:
		if local.get() == 1:
			process = subprocess.Popen([python_string, './cannon.py', '--local'])
			print("Starting local subprocess")
		else:
			process = subprocess.Popen([python_string, './cannon.py'])
		gui_status = 1
		process_name = "Cannon Main Controller"

def gm_callback():
	global local
	global process
	global gui_status
	global main_status
	global gm_status
	global process_name
	if gui_status == 0 and gm_status == 0:
		if local.get() == 1:
			print("Starting local subprocess")

			process = subprocess.Popen([python_string, './game_master.py', '--local'])
		else:
			process = subprocess.Popen([python_string, './game_master.py'])
		gui_status = 1
		process_name = "Game Master Main Controller"

def main():
	global local
	global mqtt_manager
	global gui_status
	global notification_text
	global process_name
	global py3
	global python_string
	if (mqtt_manager.target_check("laptop")):
		main_status = 1
		wallu_button.config(state=tk.DISABLED)
	else:
		main_status = 0
		wallu_button.config(state=tk.NORMAL)
	if (mqtt_manager.target_check("cannon")):
		cannon_status = 1
		cannon_button.config(state=tk.DISABLED)
	else:
		cannon_status = 0
		cannon_button.config(state=tk.NORMAL)
	if (mqtt_manager.target_check("game_master")):
		gm_status = 1
		gm_button.config(state=tk.DISABLED)
	else:
		gm_status = 0
		gm_button.config(state=tk.NORMAL)
	if py3.get() == 1:
		python_string = "python3"
	else:
		python_string = "python"

	if gui_status == 0:
		pass
	if gui_status == 1:
		global process
		if process.poll() == None:
			notification_string = process_name + " is being ran"
			notification_text.config(text=notification_string)
		else:
			notification_text.config(text="Program has terminated")
			gui_status = 0
	window.after(200, main)



# GUI State, only allows one process to be ran at a time
gui_status = 0

# MQTT Controller Statuses
main_status = 0
cannon_status = 0
gm_status = 0

# Strings
process_name = ""
python_string = "python"
window = tk.Tk(className=' WALL-U GUI')
window.configure(bg='black')

# MQTT Communication
mqtt_id = "start_menu"
mqtt_targets = ["laptop", "cannon", "game_master"]
mqtt_topics = ["pulse"]

mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, \
	targets=mqtt_targets, topics=mqtt_topics, callback=mqtt_callback, alpha=True)
mqtt_manager.start_reading()

# ===== Setup GUI =====

# Frames
top_frame = tk.Frame(master=window, width=1000, height=500)
button_frame = tk.Frame(master=window, width=500, height=100)
notification_frame = tk.Frame(master=window, width=500, height=100)
status_frame = tk.Frame(master=window, width=500, height=100)
local_frame = tk.Frame(master=window, width=500, height=100)
python3_frame = tk.Frame(master=window, width=500, height=100)

# Text
title_text = tk.Label(master=top_frame,text="WALL-U Controller Select",\
 bg="black", fg="white",padx=80,pady=30)
notification_text = tk.Label(master=notification_frame,text="",\
 bg="black", fg="white")

# Buttons
wallu_button = tk.Button(
	master=button_frame,
	text="WALL-U",
	width=10,
	height=3,
	command=wallu_callback,
	state=tk.NORMAL)
cannon_button = tk.Button(
	master=button_frame,
	text="Cannon",
	width=10,
	height=3,
	command=cannon_callback,
	state=tk.DISABLED)
gm_button = tk.Button(
	master=button_frame,
	text="GM",
	width=10,
	height=3,
	command=gm_callback,
	state=tk.DISABLED)

# Checkbox Variables
local = tk.IntVar()
py3 = tk.IntVar()
local_check = tk.Checkbutton(master=local_frame, \
	text='Local?',variable=local, bg="black",fg="white",\
	onvalue=1, offvalue=0)
python_check = tk.Checkbutton(master=python3_frame, \
	text='Python3?',variable=py3, bg="black",fg="white",\
	onvalue=1, offvalue=0)

# Packing
top_frame.pack()
title_text.pack()
button_frame.pack(fill=tk.Y)
wallu_button.pack(side=tk.LEFT)
cannon_button.pack(side=tk.LEFT)
gm_button.pack(side=tk.LEFT)
notification_frame.pack()
notification_text.pack()
#status_frame.pack()
#status_text.pack()
local_frame.pack()
local_check.pack()
python3_frame.pack()
python_check.pack()
#dead_text.pack()

window.after(200, main)

window.mainloop()
