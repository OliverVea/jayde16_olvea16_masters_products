import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity

class InstanceRecognizer():
    def __init__(self, bbox_expansion_pct, loop_closure_certainty, codebook):
        self.bbox_exp_pct = bbox_expansion_pct
        self.lc_certainty = loop_closure_certainty
        self.codebook = codebook
        self.n_landmarks = 0
        self.histograms = {}
        self.loop_closures = {}
        self.surf = cv2.xfeatures2d.SURF_create(500)
        
    def _create_mask(self, img, bbox):
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        x1, y1, x2, y2 = bbox
        x_exp = self.bbox_exp_pct * (x2-x1)
        y_exp = self.bbox_exp_pct * (y2-y1)
        cv2.rectangle(mask, (int(x1 - x_exp), int(y1 + y_exp)), (int(x2 + x_exp), int(y2 + y_exp)), (255), thickness=-1)
        return mask

    def _sample_descriptors(self, img, bbox, good_features_to_track = False):
        mask = self._create_mask(img, bbox)

        if good_features_to_track:
            good_features = cv2.goodFeaturesToTrack(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1000, 0.01, 1, mask=mask)
            kps = [cv2.KeyPoint(x=ft[0][0], y=ft[0][1], _size=20) for ft in good_features]
            _, des = self.surf.compute(kps, None)
        else:
            _, des = self.surf.detectAndCompute(img, mask)

        return des

    def _create_histogram(self, des):
        num_feat = des.shape[0]
        
        des = np.dstack(np.split(des, num_feat))
        words_stack = np.dstack([self.codebook] * num_feat) 

        diff = words_stack - des
        dist = np.linalg.norm(diff, axis=1)
        idx = np.argmin(dist, axis=0)
        hist, _ = np.histogram(idx, bins=self.codebook.shape[0])
        return hist

    def bow_comparison(self, hist, obj_name):
        max_sim = 0
        best_match = None
        for key, val in zip(self.histograms.keys(), self.histograms.values()):
            if key.split('_')[0] == obj_name:
                hist = np.reshape(hist, (1, -1))
                cos_sim = cosine_similarity(hist, val)
                if max(cos_sim[0]) > max_sim:
                    max_sim = max(cos_sim[0])
                    best_match = key
        return best_match, max_sim

    def loop_closure(self, img, bbox, obj_name, certainty=1, frame=None):
        des = self._sample_descriptors(img, bbox)
        hist = self._create_histogram(des)
        best_match, sim = self.bow_comparison(hist, obj_name)

        if sim > self.lc_certainty:
            self.histograms[best_match].append(hist)
            if frame != None:
                self.loop_closures[best_match].append(frame)
        else:
            new_landmark = f'{obj_name}_{self.n_landmarks}'
            self.histograms[new_landmark] = [hist]
            self.n_landmarks += 1
            if frame != None:
                self.loop_closures[new_landmark] = [frame]

def xywhn2xyxy(x, w=640, h=480):
    y = np.copy(x)
    y[0] = w * (x[0] - x[2] / 2) # top left x
    y[1] = h * (x[1] - x[3] / 2) # top left y
    y[2] = w * (x[0] + x[2] / 2) # bottom right x
    y[3] = h * (x[1] + x[3] / 2) # bottom right y
    return y

codebook = np.load('visual_words_100.npy')

ir = InstanceRecognizer(bbox_expansion_pct=0.5, loop_closure_certainty=0.8, codebook=codebook)

import pandas as pd
path = 'C:/Users/Jakob/Documents/Master Thesis/SLAM/Tracking/undistorted/'
df = pd.read_csv('output.csv')

names = ['Light Fixture']
for i, row in df.iterrows():

    img_path = path + str(row.image) + '.png'
    
    img = cv2.imread(img_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #cv2.imshow(str(row.image), img)
    #cv2.waitKey()
    #cv2.destroyAllWindows() 

    det = np.array([row.x, row.y, row.w, row.h])
    bbox = xywhn2xyxy(det)

    obj_name = names[row.category]

    #ir.loop_closure(img_gray, bbox, obj_name, frame=row.image)

print(ir.loop_closures.values())