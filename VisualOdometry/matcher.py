import numpy as np
import cv2

class FeatureMatcher():
    def __init__(self, K):
        self.orb = cv2.ORB_create()
        self.bf = cv2.BFMatcher(normType=cv2.NORM_HAMMING)
        self.K = K
        self.K_inv = np.linalg.inv(K)

    def extract_keypoints(self, img):
        # detection
        good_features = cv2.goodFeaturesToTrack(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1000, 0.01, 3)

        # extraction
        kps = [cv2.KeyPoint(x=ft[0][0], y=ft[0][1], size=20) for ft in good_features]
        kps, des = self.orb.compute(img, kps)

        return kps, des

    def match_and_filter(self, kps1, des1, kps2, des2, trials, threshold_lowes, threshold_dist_f, threshold_ransac, verbose):        
        all_matches = self.bf.knnMatch(des1, des2, k=2)
        E = None
        while E is None:

            matches = all_matches

            # Lowe's ratio test
            n = len(matches)
            matches = [m[0] for m in matches if m[0].distance < threshold_lowes * m[1].distance]
            if verbose: print(f'Removed {n - len(matches)} matches using Lowes ratio test (threshold: {threshold_lowes})')

            # Feature distance filter
            n = len(matches)
            matches = sorted(matches, key=lambda m: m.distance)
            matches = matches[:int(len(matches)*threshold_dist_f)]
            if verbose: print(f'Removed {n - len(matches)} matches using distance filter (threshold: {threshold_dist_f})')

            # filter using fundamental matrix
            pts1 = np.array([kps1[m.queryIdx].pt for m in matches])
            pts2 = np.array([kps2[m.trainIdx].pt for m in matches])

            pts1 = cv2.undistortPoints(pts1, cameraMatrix=self.K, distCoeffs=None)
            pts2 = cv2.undistortPoints(pts2, cameraMatrix=self.K, distCoeffs=None)

            n = len(matches)
            try:
                E, mask = cv2.findEssentialMat(pts1, pts2, np.eye(3), cv2.RANSAC, 0.999, threshold_ransac)
            except:
                E = None
                threshold_ransac *= 1.5
                threshold_lowes *= 1.1
                print(f'Failed to estimate Essential Matrix, trying again with threshold_ransac set to: {threshold_ransac} and threshold_lowes set to: {threshold_lowes}')

        if verbose: print(f'Removed {n - len(matches)} matches using Essential Matrix filter (threshold: {threshold_ransac}, trials: {trials})')
        if verbose: print(f'{len(matches)} matches left.')

        return matches, E, mask, pts1, pts2

    def get_matches(self, img1, img2, trials, threshold_lowes=0.9, threshold_dist_f=0.95, threshold_ransac=0.005, verbose=False):
        kps1, des1 = self.extract_keypoints(img1)
        kps2, des2 = self.extract_keypoints(img2)
        return self.match_and_filter(kps1, des1, kps2, des2, trials, threshold_lowes=threshold_lowes, threshold_dist_f=threshold_dist_f, 
                                    threshold_ransac=threshold_ransac, verbose=verbose)