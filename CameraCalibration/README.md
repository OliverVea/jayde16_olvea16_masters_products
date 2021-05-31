Content overview:

- calibration_images

The images used for calibration in camera.py.

- angle_image.png

Image used to display rotations around the y-axis in camera.py.

- batch_transform_images.py

Python script transforming images in the folder ./images/in and outputting them in ./images/out.
Final image size (image_size) and FOV (image_fov) can be set in the script file.

- batch_transform_videos.py

Python script transforming videos in the folder ./videos if the filename starts with '!'.
Final image size (image_size) and FOV (image_fov) can be set in the script file.

- calibration_file.npy

Numpy file containing the calibrated camera coefficients

- camera.py

Python module containing methods to calibrate a camera model [calibrate()], use it for undistortion [transform_image()], and save [save()] and load [load()] it as needed. The file is loosely based on a script made in an earlier semester project (https://github.com/SimonLBSoerensen/Flexible-Camera-Calibration/blob/master/flexiblecc/Parametric/).
