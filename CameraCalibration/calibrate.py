# This file is reused from an earlier project, can be found on: https://github.com/SimonLBSoerensen/Flexible-Camera-Calibration/blob/master/flexiblecc/Parametric/

import cv2
import numpy as np
from tqdm import tqdm
from collections.abc import Iterable
import os
from camera import CameraModels

def calibrate_camera_chessboard(gray_imgs, pattern_size, win_size=(10, 10), zero_zone=(-1, -1), criteria=None,
                     flags=(cv2.CALIB_RATIONAL_MODEL +
                            cv2.CALIB_THIN_PRISM_MODEL +
                            cv2.CALIB_TILTED_MODEL), verbose=0, draw_chessboards=None, calibration_type=None):

    assert isinstance(gray_imgs, Iterable), "gray_imgs has to be a iterable there consists of the grayscale images"
    assert len(pattern_size) == 2 and isinstance(pattern_size, tuple), "pattern_size has to be a tuple of length 2"
    assert len(win_size) == 2 and isinstance(win_size, tuple), "win_size has to be a tuple of length 2"
    assert len(zero_zone) == 2 and isinstance(zero_zone, tuple), "zero_zone has to be a tuple of length 2"

    if criteria is None:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    else:
        assert isinstance(criteria, tuple), "criteria has to be a tuple"

    if draw_chessboards is not None:
        os.makedirs(draw_chessboards, exist_ok=True)

    # Object points for a chessboard
    objp = np.zeros((1, np.product(pattern_size[:2]), 3), np.float32)
    objp[0, :, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].transpose().reshape(-1, 2)

    # Arrays to hold the object points and corner point for all the chessboards
    obj_points = []
    img_points = []
    not_used = []

    if verbose == 1:
        iter = tqdm(gray_imgs, unit="image")
        print("Finding chessboard pattern in the images")
    else:
        iter = gray_imgs
    
    iter = tqdm(iter, total=len(gray_imgs), unit="image")

    for i, gray_img in enumerate(iter):
        # Find roof corners in the images
        # pattern_was_found, corners = cv2.findChessboardCorners(gray_img, pattern_size)

        pattern_was_found, corners = cv2.findChessboardCorners(gray_img, pattern_size, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE+cv2.CALIB_CB_FILTER_QUADS)

        # If there was a chessboard in the image
        if pattern_was_found:
            # Add object points for the chessboard
            obj_points.append(objp)

            # Find better sub pix position for the corners in the roof corners neighbourhood
            new_better_corners = cv2.cornerSubPix(gray_img, corners, win_size, zero_zone, criteria)

            if draw_chessboards is not None:
                #img_first = cv2.drawChessboardCorners(gray_img.copy(), pattern_size, corners,
                #                                       pattern_was_found)
                img_better = cv2.drawChessboardCorners(gray_img.copy(), pattern_size, new_better_corners,
                                                       pattern_was_found)
                #cv2.imwrite(os.path.join(draw_chessboards, "{}_first.png".format(i)), img_first)
                cv2.imwrite(os.path.join(draw_chessboards, "{}.png".format(i)), img_better)

            # Add the better corners
            img_points.append(new_better_corners)
        else:
            not_used.append(i)
    if verbose == 1:
        print("Doing camera calibration")

    # Do the camera calibrations from the object points and corners found in the images

    if calibration_type in [CameraModels.FISHEYE, CameraModels.FISHEYE]:
        N_OK = len(obj_points)
        rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
        tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
        K = np.zeros((3, 3))
        if calibration_type == CameraModels.FISHEYE:
            D = np.zeros((4, 1))
            calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC+cv2.fisheye.CALIB_CHECK_COND
            retval, K, D, rvecs, tvecs = cv2.fisheye.calibrate(objectPoints=obj_points, imagePoints=img_points, 
                image_size=(gray_imgs[0].shape[1], gray_imgs[0].shape[0]), K=K, D=D, rvecs=rvecs, tvecs=tvecs, 
                flags=calibration_flags, criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))
        else:
            D = np.zeros((1, 4))
            xi = np.array([])
            idx = np.array([])
            calibration_flags = cv2.omnidir.RECTIFY_PERSPECTIVE
            retval, K, xi, D, rvecs, tvecs, idx	= cv2.omnidir.calibrate(objectPoints=obj_points, imagePoints=img_points, 
            size=(gray_imgs[0].shape[1], gray_imgs[0].shape[0]), K=K, xi=xi, D=D, flags=calibration_flags, 
            criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))
    else:
        retval, cameraMatrix, distCoeffs, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors = cv2.calibrateCameraExtended(
            obj_points, img_points, (gray_imgs[0].shape[1], gray_imgs[0].shape[0]), cameraMatrix=None, distCoeffs=None, flags=flags)


    obj_points, img_points, not_used = np.array(obj_points), np.array(img_points), np.array(not_used)
    obj_points = obj_points.reshape((obj_points.shape[0], obj_points.shape[2], obj_points.shape[3]))
    obj_points_temp = np.ndarray(obj_points.shape[0], dtype='object')
    img_points_temp = np.ndarray(img_points.shape[0], dtype='object')
    for i in range(len(obj_points)):
        obj_points_temp[i] = obj_points[i]
    for i in range(len(img_points)):
        img_points_temp[i] = img_points[i]

    if calibration_type == CameraModels.FISHEYE:
        return retval, K, D, rvecs, tvecs, obj_points_temp, img_points_temp, not_used
    elif calibration_type == CameraModels.OMNIDIR:
        retval, K, xi, D, rvecs, tvecs, idx, obj_points_temp, img_points_temp, not_used
    else:
        return retval, cameraMatrix, distCoeffs, rvecs, tvecs, stdDeviationsIntrinsics, stdDeviationsExtrinsics, perViewErrors, obj_points_temp, img_points_temp, not_used