import sys
import os
import threading
import time
import paho.mqtt.client as mqtt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
                             QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QSlider)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..')))
from comms.mqtt import interface as mqtt_interface


max_value = 255
current_hue = 0
current_sat = 0
current_val = 0

current_low_hue = 0
current_low_sat = 0
current_low_val = 0

class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        grid = QGridLayout()
        grid.addWidget(self.HueSlider(), 0, 0)
        grid.addWidget(self.SatSlider(), 0, 1)
        grid.addWidget(self.ValSlider(), 0, 2)
        grid.addWidget(self.LowHueSlider(), 1, 0)
        grid.addWidget(self.LowSatSlider(), 1, 1)
        grid.addWidget(self.LowValSlider(), 1, 2)
        self.setLayout(grid)

        self.setWindowTitle("PyQt5 Sliders")
        self.resize(400, 300)

    def createExampleGroup(self):
        groupBox = QGroupBox("Slider Example")

        radio1 = QRadioButton("&Radio horizontal slider")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def HueSlider(self):
        groupBox = QGroupBox("Hue Slider")

        radio1 = QRadioButton("&Radio horizontal slider")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        slider.valueChanged[int].connect(self.changeHue)

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def changeHue(self, value):
        global current_hue
        current_hue = max_value*(value/100)
        current_hue = int(current_hue)
        #print(current_value)

    def LowHueSlider(self):
        groupBox = QGroupBox("Hue Slider")

        radio1 = QRadioButton("&Radio horizontal slider")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        slider.valueChanged[int].connect(self.changeLowerHue)

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def changeLowerHue(self, value):
        global current_low_hue
        current_low_hue = max_value*(value/100)
        current_low_hue = int(current_low_hue)
        #print(current_value)

    def SatSlider(self):
        groupBox = QGroupBox("Saturation Slider")

        radio1 = QRadioButton("&Radio horizontal slider")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        slider.valueChanged[int].connect(self.changeSat)


        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def changeSat(self, value):
        global current_sat
        current_sat = max_value*(value/100)
        current_sat = int(current_sat)
        #print(current_value)

    def LowSatSlider(self):
        groupBox = QGroupBox("Hue Slider")

        radio1 = QRadioButton("&Radio horizontal slider")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        slider.valueChanged[int].connect(self.changeLowerSat)

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def changeLowerSat(self, value):
        global current_low_sat
        current_low_sat = max_value*(value/100)
        current_low_sat = int(current_low_sat)
        #print(current_value)

    def ValSlider(self):
        groupBox = QGroupBox("Value Slider")

        radio1 = QRadioButton("&Radio horizontal slider")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        slider.valueChanged[int].connect(self.changeVal)


        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def changeVal(self, value):
        global current_val
        current_val = max_value*(value/100)
        current_val = int(current_val)
        #print(current_value)

    def LowValSlider(self):
        groupBox = QGroupBox("Hue Slider")

        radio1 = QRadioButton("&Radio horizontal slider")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        slider.valueChanged[int].connect(self.changeLowerVal)

        radio1.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(slider)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)

        return groupBox

    def changeLowerVal(self, value):
        global current_low_val
        current_low_val = max_value*(value/100)
        current_low_val = int(current_low_val)
        #print(current_value)

def print_val():
    global current_hue
    while(1):
        print(str(current_hue) + " " + str(current_sat))

def on_connect():
    print("Connecting to server")

def on_message_print(client, userdata, message):
    payload = message.payload.decode('utf-8')
    #new_values = payload.split()
    #new_values = message.payload.split(",")
    new_values = payload.split(",")
    hue = int(new_values[0], 16)
    sat = int(new_values[1], 16)
    val = int(new_values[2], 16)
    l_hue = int(new_values[3], 16)
    l_sat = int(new_values[4], 16)
    l_val = int(new_values[5], 16)
    #hue = int((payload[0]).decode("utf-8"))
    print("%s %x %x %x %x %x %x" % (message.topic, hue, sat, val, l_hue, l_sat, l_val))

def publish_values():
    global current_hue
    global current_sat
    mqtt_id = "thresholds"
    mqtt_topics = ["upper_thresh"]
    mqtt_manager = mqtt_interface.MqttInterface(id=mqtt_id, targets=[], topics=mqtt_topics, callback=on_message_print, local= False)
    mqtt_manager.start_reading()
    while True:
        hue = current_hue
        sat = current_sat
        val = current_val
        hue = str(hue)
        sat = str(sat)
        val = str(val)
        l_hue = current_low_hue
        l_sat = current_low_sat
        l_val = current_low_val
        l_hue = str(l_hue)
        l_sat = str(l_sat)
        l_val = str(l_val)
        thresholds = hue + "," + sat + "," + val + "," + l_hue + "," + l_sat + "," + l_val
        mqtt_manager.send_message("upper_thresh", thresholds)
        time.sleep(1)
    '''
    mqtt_client = mqtt.Client("Thresholds")
    mqtt_client.on_message = on_message_print
    # Connect to broker
    #mqtt_client.connect("192.168.1.184")
    #mqtt_client.connect("mqtt.eclipse.org", 1883, 60)
    mqtt_client.connect_async("mqtt.eclipse.org")
    mqtt_client.loop_start()
    hue = current_hue
    sat = current_sat
    hue = str(hue)
    sat = str(sat)
    thresholds = hue + " " + sat
    mqtt_client.subscribe("upper/thresh")
    mqtt_client.publish("upper/thresh", thresholds)
    time.sleep(4)
    mqtt_client.loop_stop()
    print("Got here")
    '''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    x = threading.Thread(target=publish_values, daemon = False)
    x.start()
    app.exec_()
    x.join()