# Heartbeat-monitor
Aimed at developing an embedded device capable of measuring heart rate and heart rate variability using photoplethysmography (PPG) and a Raspberry Pi Pico W microcontroller. 

The hardware used for the project: 
1.	Raspberry Pi Pico W- https://www.raspberrypi.com/products/raspberry-pi-pico/
2.	Crowtail Pulse Sensor v2.0- https://www.elecrow.com/crowtail-pulse-sensor-p-1673.html
3.	OLED display- https://www.electronicwings.com/sensors-modules/ssd1306-oled-display
4.	Protoboard - Passive protoboard designed for this project to help connect other components to the Raspberry Pi Pico. (Joseph Hotchkiss, Project Engineer, Metropolia UAS)
5.	Rotary encoder with push button (Joseph Hotchkiss, Project Engineer, Metropolia UAS)

The software used for implementation:
1.	Micro python- https://micropython.org/
2.	Thonny IDE- https://thonny.org/
3.	Kubios Cloud (Optional)- https://www.kubios.com/kubios-cloud/

![image](https://github.com/hoodahim/Heartbeat-monitor/assets/111939973/9cf40e36-cb70-4bba-a943-2dd269ba38b4)


A detailed description of the project understanding can be read from:
https://github.com/hoodahim/Heartbeat-monitor/blob/main/G7%20Final%20Project%20Report.pdf


### Implementation on raspberry pi 

Upload the HeartRate-Monitor.py file to raspberry pi and rename the file as main (this will allow to run the program on powerup)

Additional libraries are also need to run the program which can be downloaded from this link

https://gitlab.metropolia.fi/lansk/picow-mip-example

![image](https://github.com/hoodahim/Heartbeat-monitor/assets/111939973/08882011-aea5-49ac-8c55-6135465baefb)
