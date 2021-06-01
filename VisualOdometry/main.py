import cv2
import numpy as np
import glob
import random
from visual_odometry import VisualOdometry
from utility import *
from scipy.spatial.transform import Rotation as R

# Seed is set to ensure reproducibility
np.random.seed(0)
random.seed(0)
cv2.setRNGSeed = 0

# Image parameters
image_width = 640
image_height = 480
fov_x = 150
fov_y = 120

# Defining intrinsic matrix
K = np.eye(3)
K[0,0] = image_width / np.tan(fov_x  / 180 * np.pi / 2) / 2
K[1,1] = image_height / np.tan(fov_y / 180 * np.pi / 2) / 2
K[0,2] = image_width / 2
K[1,2] = image_height / 2

# Number of trials depends on the expected outlier rate and how often RANSAC has to succeed to be good enough.
# trials = ceil(np.log(1 - 0.99999) / np.log(1 - (1 - 0.066)**8))
ransac_trials = 100 # This is chosen arbitrarily, but doesn't take too long and gives decent results.

# Load images in correct order
img_offset = 0 # Offset images to use from dataset.
img_step = 1 # Use every img_step image from the dataset (if img_step=2, every other image is used).
img_files = glob.glob('images/*.PNG')
sorted_idxs = np.argsort([int(file.split('\\')[-1].split('.')[0]) for file in img_files]) # Needed due to lack of zero-padding in filenames
img_files = [img_files[idx] for idx in sorted_idxs]
images = [cv2.imread(img) for img in img_files[img_offset:200:img_step]]

imu_file='imu.csv'
gnss_file='gnss.csv'
draw_matches = False
verbose = True

imu_orientations = get_orientations(imu_file, gnss_file)
scales, first_coord = get_scale_and_coord(gnss_file, img_offset, img_step)

start_pose = np.eye(4)
start_pose[:3,:3] = imu_orientations[img_offset]
route = [start_pose]

vo = VisualOdometry(K, ransac_trials=ransac_trials)

for i, img in enumerate(images[1:]): 
    transform, matches, kps1, kps2 = vo.calculate_transform(images[i], images[i + 1], scale=scales[img_offset + i])
    
    last_transform = route[i]
    last_transform[:3,:3] = imu_orientations[img_offset + i]
    route.append(np.dot(last_transform, transform))

    # Draw matches
    if draw_matches:
        img_matches = cv2.drawMatches(img, kps1, images[i], kps2, matches, None,
                                      flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        cv2.imshow('Matches', img_matches)
        cv2.waitKey(0)

    if verbose:
        if i % 100 == 0:
            print(f'{i} frames processed.')

#np.save('vo_route_imu.npy',route)
#route = np.load('vo_route_imu.npy', allow_pickle=True)

#save_route_as_csv(route=route, filename='vo_route_5point_imu', first_coord=first_coord)
plot_route(route, projection='2d', first_coord=[first_coord[0], 0, first_coord[1]])