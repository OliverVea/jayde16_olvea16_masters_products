import numpy as np
import cv2

from sklearn.cluster import KMeans

class BagOfWords():
    def __init__(self, K, features=[], random_state=None, verbose=0):
        self.K = K
        self.features = features
        self.sift = cv2.SIFT_create()
        self.kmeans = KMeans(n_clusters=self.K, random_state=random_state, verbose=verbose)
    
    def add_features(self, img):
        good_features = cv2.goodFeaturesToTrack(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1000, 0.01, 3)
        kps = [cv2.KeyPoint(x=ft[0][0], y=ft[0][1], _size=20) for ft in good_features]
        kps, des = self.sift.compute(img, kps)
        if des is not None:
            for d in des:
                self.features.append(d)
        return kps, des

    def fit_clusters(self):
        self.kmeans.fit(self.features)
        return self.kmeans

    def get_clusters(self):
        return self.kmeans

    def get_features(self):
        return self.features

features = np.load('sift_features.npy', allow_pickle=True)

bow = BagOfWords(K=1000, features=features, random_state=0, verbose=1)

kmeans = bow.fit_clusters()

clusters = kmeans.cluster_centers_

np.save('kmeans_1000.npy', kmeans)
np.save('visual_words_1000.npy', clusters)