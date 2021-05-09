import os
import calibrate
import rtvecs_illustration

datasetpath = "30mmfinal/*"

import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
import shutil

image_files = glob.glob(datasetpath)

color_images = [cv2.imread(f) for f in tqdm(image_files)]

greyscale_images = [cv2.cvtColor(c_img, cv2.COLOR_BGR2GRAY) for c_img in tqdm(color_images)]

image_shape = color_images[0].shape[:2]

exception_thrown = True
while exception_thrown:
    try:
        retval, K, D, rvecs, tvecs, obj_points_temp, img_points_temp, not_used = calibrate.calibrate_camera_chessboard(greyscale_images, (5,8), verbose=1)
        exception_thrown = False
    except Exception as e:
        if image_files is not None:
            i = int(e.err.split(' ')[-1])
            shutil.move(image_files[i], '30mmcalibcheckcond/' + image_files[i].split('\\')[1])
            del greyscale_images[i]
            del image_files[i]
        print(e)

np.save('30mm_calibration_params_fixed.npy', np.array([retval, K, D, rvecs, tvecs, obj_points_temp, img_points_temp, not_used], dtype='object'))
#retval, K, D, rvecs, tvecs, obj_points_temp, img_points_temp, not_used = np.load('30mm_calibration_params.npy')

#retval, K, xi, D, rvecs, tvecs, idx, obj_points_temp, img_points_temp, not_used = calibrate.calibrate_camera_chessboard(greyscale_images, (5,8), verbose=1)
#np.save('30mm_omnidir_cylind_small_calibration_params.npy', np.array([retval, K, xi, D, rvecs, tvecs, idx, obj_points_temp, img_points_temp, not_used], dtype='object'))


#cv2.fisheye.undistortImage()


'''
for i, img in enumerate(color_images):
    if i not in not_used:
        cv2.imwrite('30mmdetected/' + image_files[i].split('\\')[1], img)



calibrate_retval_5dp, cameraMatrix_5dp, distCoeffs_5dp, rvecs_5dp, tvecs_5dp, stdDeviationsIntrinsics_5dp, stdDeviationsExtrinsics_5dp, \
    perViewErrors_5dp, charucoCorners_all_5dp, charucoIds_all_5dp, markerCorners_all_5dp, armarkerIds_all_5dp, obj_points_all_5dp, board, _ = calibrate.calibrate_camera_charuco(greyscale_images, squaresX, squaresY,
                                                                                                                                                  squareLength, markerLength, dictionary, flags=0, verbose=1)

np.save('camera_calibration_5dp_small.npy', [calibrate_retval_5dp, cameraMatrix_5dp, distCoeffs_5dp, rvecs_5dp, tvecs_5dp, 
stdDeviationsIntrinsics_5dp, stdDeviationsExtrinsics_5dp, perViewErrors_5dp, charucoCorners_all_5dp, 
charucoIds_all_5dp, markerCorners_all_5dp, armarkerIds_all_5dp, obj_points_all_5dp])

calibrate_retval_14dp, cameraMatrix_14dp, distCoeffs_14dp, rvecs_14dp, tvecs_14dp, stdDeviationsIntrinsics_14dp, stdDeviationsExtrinsics_14dp, \
    perViewErrors_14dp, charucoCorners_all_14dp, charucoIds_all_14dp, markerCorners_all_14dp, armarkerIds_all_14dp, obj_points_all_14dp, board, _ = calibrate.calibrate_camera_charuco(greyscale_images, squaresX, squaresY,
                                                                                                                                                  squareLength, markerLength, dictionary, verbose=1, draw='charuco/')

np.save('camera_calibration_14dp_small.npy', [calibrate_retval_14dp, cameraMatrix_14dp, distCoeffs_14dp, rvecs_14dp, tvecs_14dp, 
    stdDeviationsIntrinsics_14dp, stdDeviationsExtrinsics_14dp, perViewErrors_14dp, charucoCorners_all_14dp, 
    charucoIds_all_14dp, markerCorners_all_14dp, armarkerIds_all_14dp, obj_points_all_14dp])

rtvecs_illustration.draw_rtvecs(rvecs_14dp, tvecs_14dp, obj_points_all_14dp)
plt.title("Board placement")
plt.tight_layout()
plt.show()

for img, corners in zip(color_images, charucoCorners_all_14dp):
    for i, point in enumerate(corners):
        c = i / len(corners)
        cv2.circle(img, (point[0][0], point[0][1]), 5, (255*c,0,(1-c)*255), -1)

    cv2.imshow("test",img)
    cv2.waitKey()
'''