Folder containing the Jetson programming used for the results of the project.

- main.py

The main file of the program which is run by the Jetson Nano on reboot.

- task.py

A file containing the definition of the Task class, which the task files inherit from.

- event.py

A file containing the code used  to subscribe to and broadcast events.

- pipeline.py

Contains the code for the Accellerated GStreamer pipeline.

Task files:

- imu.py

File containing the code used to connect to and handle the IMU data.

- led.py

File containing code used for the logic behind the LEDs.

- serial_task.py

Contains the code used to read the GNSS data.

- switch.py

File used to handle reading switches.

- video.py

File used to read the GStreamer pipeline and save the images.

- webserver.py

File used to read the GStreamer pipeline and forward it to another device using a WebGear.
