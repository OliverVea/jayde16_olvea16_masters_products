import cv2
import numpy as np

from math import sin, cos, pi

from enum import Enum

class CameraModels(Enum):
    DEFAULT = 0
    FISHEYE = 1
    OMNIDIR = 2

class Camera:
    def __init__(self, camera_matrix, distortion_coefficients, camera_model = CameraModels.DEFAULT, retval=None, rvecs=None, tvecs=None):
        self.K = camera_matrix
        self.d = distortion_coefficients
        self.model = camera_model
        self.retval = retval
        self.rvecs = rvecs
        self.tvecs = tvecs

    @staticmethod
    def calibrate(images: list, pattern_size: tuple, camera_model = CameraModels.DEFAULT):
        object_points = np.zeros((1, np.product(pattern_size[:2]), 3), np.float32)
        object_points[0, :, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].transpose().reshape(-1, 2)

        obj_points = []
        img_points = []
        unused_images = []

        print('Identifying checkerboard corners:')
        for i, image in enumerate(tqdm(images, total=len(images), unit="image")):
            pattern_was_found, corners = cv2.findChessboardCorners(image, pattern_size, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FILTER_QUADS)
            
            if pattern_was_found:
                obj_points.append(object_points)

                new_better_corners = cv2.cornerSubPix(image=image, 
                    corners=corners, 
                    winSize=(10, 10), 
                    zeroZone=(-1, -1), 
                    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

                img_points.append(new_better_corners)

            else:
                unused_images.append(i)

        if camera_model == CameraModels.DEFAULT:
            print('Calibrating camera with default model.')
            
            flags = cv2.CALIB_RATIONAL_MODEL + cv2.CALIB_THIN_PRISM_MODEL + cv2.CALIB_TILTED_MODEL

            retval, K, D, rvecs, tvecs = cv2.calibrateCamera(objectPoints=obj_points, 
                imagePoints=img_points, 
                imageSize=(images[0].shape[1], images[0].shape[0]), 
                cameraMatrix=None, 
                distCoeffs=None, 
                flags=flags)
        
        elif camera_model == CameraModels.FISHEYE:
            print('Calibrating camera with fisheye model.')

            flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND

            retval, K, D, rvecs, tvecs = cv2.fisheye.calibrate(
                objectPoints=obj_points, 
                imagePoints=img_points, 
                image_size=(images[0].shape[1], images[0].shape[0]), 
                K=np.zeros((3, 3)), 
                D=np.zeros((4, 1)), 
                rvecs=[np.zeros((1, 1, 3), dtype=np.float64) for _ in obj_points], 
                tvecs=[np.zeros((1, 1, 3), dtype=np.float64) for _ in obj_points], 
                flags=flags, 
                criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6))

        elif camera_model == CameraModels.OMNIDIR:
            print('Calibrating camera with omnidir model.')
            pass

        else:
            raise Exception('camera_model not valid.')

        camera = Camera(camera_matrix=K, distortion_coefficients=D, camera_model=camera_model, retval=retval, rvecs=rvecs, tvecs=tvecs)
        return camera

    @staticmethod
    def load(file):
        camera_matrix, distortion_coefficients, camera_model, retval, rvecs, tvecs = np.load(file, allow_pickle=True)

        return Camera(camera_matrix=camera_matrix, 
            distortion_coefficients=distortion_coefficients, 
            camera_model=camera_model,
            retval=retval,
            rvecs=rvecs,
            tvecs=tvecs,)

    def save(self, file):
        np.save(file, np.array([self.camera_matrix, self.distortion_coefficients, self.camera_model, self.retval, self.rvecs, self.tvecs]), dtype='object')

    def transform_image(self, input, size: tuple, fov: tuple, ax: float = 0, ay: float = 0, az: float = 0):
        input_size = (input.shape[1], input.shape[0])

        # Translating FOV from angles to radians.
        c = 1 / 2 * pi / 180
        va, ha = fov[1] * c, fov[0] * c
        
        # Edge (center-)points of ROI in 3D space
        pts = np.array([
            (sin(-ha + ay), 0, cos(-ha + ay)), 
            (sin(ha + ay), 0, cos(ha + ay)),
            (0, sin(-va + ax), cos(-va + ax)), 
            (0, sin(va + ax), cos(va + ax))])

        # Edge (center-)points in pixel coordinates
        if self.model == CameraModels.FISHEYE:
            pts, _ = cv2.fisheye.projectPoints(pts.reshape((pts.shape[0],1,3)), rvec=np.zeros((3,1)), tvec=np.zeros((3,1)), K=self.K, D=self.d)

        if self.model == CameraModels.DEFAULT:
            pts, _ = cv2.projectPoints(pts, rvec=np.zeros((3,1)), tvec=np.zeros((3,1)), cameraMatrix=self.K, distCoeffs=self.d)

        # Calculating the necessary upscaling to crop the ROI to the desired image size.
        width = max(pts[:,0,0]) - min(pts[:,0,0])
        height = max(pts[:,0,1]) - min(pts[:,0,1])
        
        scale = (size[0] / width, size[1] / height)
        uncropped_size = (int(scale[0] * input_size[0]), int(scale[1] * input_size[1]))

        # Testing rotation
        R = np.eye(3)
        Rx = [[1, 0, 0], [0, cos(ax), -sin(ax)], [0, sin(ax), cos(ax)]]
        Ry = [[cos(ay), 0, sin(ay)], [0, 1, 0], [-sin(ay), 0, cos(ay)]]
        Rz = [[cos(az), -sin(az), 0], [sin(az), cos(az), 0], [0, 0, 1]]
        R = np.dot(np.dot(np.array(Rx), np.array(Ry)), np.array(Rz))

        # Calculating new camera matrix (nK)
        if self.model == CameraModels.FISHEYE:
            nK = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(K=self.K, D=self.d, image_size=input_size, new_size=uncropped_size, R=np.eye(3))

        if self.model == CameraModels.DEFAULT:
            nK, _ = cv2.estimateNewCameraMatrixForUndistortRectify(cameraMatrix=self.K, distCoeffs=self.d, imageSize=input_size, newImgSize=uncropped_size, alpha=0.0)

        # Undistoring image
        if self.model == CameraModels.FISHEYE:
            map1, map2 = cv2.fisheye.initUndistortRectifyMap(K=self.K, D=self.d, R=R, P=nK, size=uncropped_size, m1type=cv2.CV_32FC1)

        if self.model == CameraModels.DEFAULT:
            map1, map2 = cv2.initUndistortRectifyMap(cameraMatrix=self.K, distCoeffs=self.d, R=R, newCameraMatrix=nK, size=uncropped_size, m1type=cv2.CV_32FC1)

        output = cv2.remap(input, map1, map2, interpolation=cv2.INTER_CUBIC)
        
        # Extracting principal point (center of camera)
        x, y = nK[0][2], nK[1][2]

        # Calculating ROI bounding box coordinates
        x1, y1, x2, y2 = x - size[0] / 2, y - size[1] / 2, x + size[0] / 2, y + size[1] / 2
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # Extracting ROI
        output = output[y1:y2, x1:x2]

        return output

if __name__ == '__main__':
    import glob
    from tqdm import tqdm
    import shutil

    datasetpath = "30mmhandpicked/*"

    image_files = glob.glob(datasetpath)

    print('Loading images:')
    color_images = [cv2.imread(f) for f in tqdm(image_files)]

    greyscale_images = [cv2.cvtColor(c_img, cv2.COLOR_BGR2GRAY) for c_img in tqdm(color_images)]

    image_shape = color_images[0].shape[:2]

    exception_thrown = True
    while exception_thrown:
        try:
            camera = Camera.calibrate(images=greyscale_images, pattern_size=(5,8), camera_model=CameraModels.FISHEYE)
            exception_thrown = False
        except Exception as e:
            if image_files is not None:
                i = int(e.err.split(' ')[-1])
                shutil.move(image_files[i], '30mmcalibcheckcond/' + image_files[i].split('\\')[1])
                del greyscale_images[i]
                del image_files[i]
            print(e)

    print(camera)

    img = cv2.imread('D:\\WindowsFolders\\Code\\Master\\jayde16_olvea16_masters_2021\\camera_calibration\\angleimages\\vlcsnap-2021-02-22-22h23m07s859.png')

    cv2.imshow('original', img)

    for i in range(6):
        im = camera.transform_image(img, (816*2/3, 616*2/3), (120, 90), ay=(i * -15 * pi / 180))
        im = cv2.line(im, (int(im.shape[1]/2), 0), (int(im.shape[1]/2), im.shape[0]), (255, 0, 0))
        cv2.imshow(f"Rotated {i * 15} degrees.", im)

    cv2.waitKey()