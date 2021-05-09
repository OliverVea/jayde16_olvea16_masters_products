Content overview:

- 30mm_calibration_params_fixed.npy

Numpy file containing the calibrated camera coefficients

- batch_transform_images.py

Python script transforming images in the folder ./images/in and outputting them in ./images/out.
Final image size (image_size) and FOV (image_fov) can be set in the script file.


- batch_transform_videos.py

Python script transforming videos in the folder ./videos if the filename starts with '!'.
Final image size (image_size) and FOV (image_fov) can be set in the script file.


- camera.py

Python module containing methods to calibrate a camera model, use it for undistortion, and save and load it as needed. The file is loosely based on a script made in an earlier semester project ().

-- calibrate()

Static method used to calibrate the camera.

-- 