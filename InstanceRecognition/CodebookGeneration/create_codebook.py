import numpy as np
import cv2

from sklearn.cluster import KMeans

class BagOfWords():
    def __init__(self, K, features=[], random_state=None, verbose=0):
        self.K = K
        self.features = features
        self.surf = cv2.xfeatures2d.SURF_create(500)
        self.kmeans = KMeans(n_clusters=self.K, random_state=random_state, verbose=verbose)
    
    def add_features(self, img):
        kps, des = self.surf.compute(img, kps)
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

features = np.load('surf_features.npy', allow_pickle=True)

print(len(features))

bow = BagOfWords(K=1000, features=features, random_state=0, verbose=1)

kmeans = bow.fit_clusters()

clusters = kmeans.cluster_centers_

np.save('kmeans_1000.npy', kmeans)
np.save('visual_words_1000_surf.npy', clusters)