import cv2
import numpy as np
from matcher import FeatureMatcher
from utility import *

class VisualOdometry():
    def __init__(self, K, ransac_trials=100):
        self.K = K
        self.all_kps = []
        self.trials=ransac_trials
        self.matcher = FeatureMatcher(K)

    def calculate_transform(self, img1, img2, scale=1.0, verbose=False):

        matches, E, mask, pts1, pts2 = self.matcher.get_matches(img1, img2, self.trials, threshold_ransac=0.005, 
                                                  threshold_lowes=0.7, verbose=verbose)

        points, rotation, translation, mask = cv2.recoverPose(E, pts1, pts2, mask=mask)
        matches = [kp for kp, inlier in zip(matches, mask) if inlier]

        #points1 = np.array([kps1[m.queryIdx].pt for m in matches])
        #points2 = np.array([kps2[m.trainIdx].pt for m in matches])

        # calculate camera pose
        #_, rotation, translation, _, _ = cv2.recoverPose(E, points1, points2, self.K, distanceThresh=10000)

        transform = np.eye(4)
        transform[:3,:3] = rotation
        transform[:3,3:] = np.dot(translation, scale)

        return transform, matches, pts1, pts2
