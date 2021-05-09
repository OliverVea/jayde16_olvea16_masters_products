from camera import Camera, CameraModels

import cv2
import numpy as np
import os

camera_model = CameraModels.FISHEYE
retval, K, d, rvecs, tvecs, obj_points_temp, img_points_temp, not_used = np.load('30mm_calibration_params_fixed.npy', allow_pickle=True)

cam = Camera(camera_matrix=K, distortion_coefficients=d, camera_model=camera_model)

image_size = (640, 480)
image_fov = (150, 120)

show_image = False

path = 'videos'

files = os.listdir(path)
files = [file for file in files if file.startswith('!')]

print(f'Found {len(files)} files:')
print('\n'.join(files))

fourcc = cv2.VideoWriter_fourcc(*'HFYU')
vw = cv2.VideoWriter()

for i, file in enumerate(files):
    print(f'Undistorting file: {file}')

    vc = cv2.VideoCapture(f'{path}/{file}')

    vw.open(f'{path}/undistorted_downscaled/{file[1:-4]}.avi', fourcc, 21, image_size)

    while True:
        success, img = vc.read()

        if not success:
            break

        img_out = cam.transform_image(img, image_size, image_fov)

        if show_image != False and (show_image == True or (isinstance(show_image, list) and show_image[i])): 
            cv2.imshow('undistorted', img_out) 
            
            if cv2.waitKey() == 27:
                break

        vw.write(img_out)

    vw.release()
    vc.release()

    os.rename(f'{path}/{file}', f'{path}/{file[1:]}')