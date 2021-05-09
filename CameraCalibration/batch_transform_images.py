from camera import Camera, CameraModels

import cv2
import numpy as np
import os

from tqdm import tqdm

camera_model = CameraModels.FISHEYE
retval, K, d, rvecs, tvecs, obj_points_temp, img_points_temp, not_used = np.load('30mm_calibration_params_fixed.npy', allow_pickle=True)

cam = Camera(camera_matrix=K, distortion_coefficients=d, camera_model=camera_model)

image_size = (640, 480)
image_fov = (150, 120)

show_image = False

path = 'D:\\WindowsFolders\\Code\\Master\\jayde16_olvea16_masters_2021\\camera_calibration\\images'

path_in = os.path.join(path, 'in/')
path_out = os.path.join(path, 'out/')

files = os.listdir(path_in)
files = [file for file in files]

#print(f'Searching: {}')

print(f'Found {len(files)} files:')
print('\n'.join(files))

fourcc = cv2.VideoWriter_fourcc(*'HFYU')
vw = cv2.VideoWriter()

for i, file in tqdm(enumerate(files), total=len(files)):
    im = cv2.imread(os.path.join(path_in, file))

    img_out = cam.transform_image(im, image_size, image_fov)

    cv2.imwrite(os.path.join(path_out, file), img_out)