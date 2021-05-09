Content overview:

- 30mm_calibration_params_fixed.npy

Numpy file containing the calibrated camera coefficients

- batch_transform_images.py

Python script transforming images in the folder ./images/in and outputting them in ./images/out.
Final image size (image_size) and FOV (image_fov) can be set in the script file.


- batch_transform_videos.py

Python script transforming videos in the folder ./videos if the filename starts with '!'.
Final image size (image_size) and FOV (image_fov) can be set in the script file.


- calibrate.py

Calibration function partly reused from an earlier semester project (https://github.com/SimonLBSoerensen/Flexible-Camera-Calibration/blob/master/flexiblecc/Parametric/).
Can calibrate on checkerboard images with either normal calibrateCameraExtended or the cv2.fisheye module. 

- calibration.py

The calibration script. Loads the images, calibrates with calibrate.py and saves the camera parameters to an external file.