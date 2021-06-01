import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity

class InstanceRecognizer():
    def __init__(self, bbox_expansion_pct, loop_closure_certainty, codebook, hessian_threshold):
        self.bbox_exp_pct = bbox_expansion_pct
        self.lc_certainty = loop_closure_certainty
        self.codebook = codebook
        self.n_landmarks = 0
        self.histograms = {}
        self.loop_closures = {}
        self.hessian_threshold = hessian_threshold
        self.surf = cv2.xfeatures2d.SURF_create(self.hessian_threshold)
        
    def _create_mask(self, img, bbox):
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        x1, y1, x2, y2 = bbox
        x_exp = self.bbox_exp_pct * (x2-x1)
        y_exp = self.bbox_exp_pct * (y2-y1)

        patch  = [int(bbox[0] - x_exp), int(bbox[1] - y_exp), int(bbox[2] + x_exp), int(bbox[3] + y_exp)]
        bbox = [int(x) for x in bbox]
        cv2.rectangle(mask, (patch[0], patch[1]), (patch[2], bbox[1]), (255), thickness=-1)
        cv2.rectangle(mask, (patch[0], bbox[1]), (bbox[0], patch[3]), (255), thickness=-1)
        cv2.rectangle(mask, (bbox[0], bbox[3]), (patch[2], patch[3]), (255), thickness=-1)
        cv2.rectangle(mask, (bbox[2], bbox[1]), (patch[2], bbox[3]), (255), thickness=-1)

        return mask

    def _sample_descriptors(self, img, bbox, hessian_threshold, good_features_to_track = False):
        mask = self._create_mask(img, bbox)

        surf = self.surf
        if hessian_threshold != self.hessian_threshold:
            surf = cv2.xfeatures2d.SURF_create(hessian_threshold)

        if good_features_to_track:
            good_features = cv2.goodFeaturesToTrack(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 1000, 0.01, 1, mask=mask)
            kps = [cv2.KeyPoint(x=ft[0][0], y=ft[0][1], _size=20) for ft in good_features]
            _, des = surf.compute(kps, None)
        else:
            _, des = surf.detectAndCompute(img, mask)

        if len(des) < 1:
            return self._sample_descriptors(img, bbox, hessian_threshold - 50, good_features_to_track = good_features_to_track)
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
        des = self._sample_descriptors(img, bbox, self.hessian_threshold)
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

    def get_similarities(self, images, bboxs, obj_name):
        for img, bbox in zip(images, bboxs):
            des = self._sample_descriptors(img, bbox, self.hessian_threshold)
            new_landmark = f'{obj_name}_{self.n_landmarks}'
            self.histograms[new_landmark] = self._create_histogram(des)
            self.n_landmarks += 1
        
        similarities = np.ndarray((len(images),len(images)))
        for i, (img, bbox) in enumerate(zip(images, bboxs)):
            des = self._sample_descriptors(img, bbox, self.hessian_threshold)
            hist = self._create_histogram(des)
            hist = np.reshape(hist, (1, -1))
            cos_sim = cosine_similarity(hist, list(self.histograms.values()))
            similarities[i] = cos_sim
        return similarities

def xywhn2xyxy(x, w=640, h=480):
    y = np.copy(x)
    y[0] = w * (x[0] - x[2] / 2) # top left x
    y[1] = h * (x[1] - x[3] / 2) # top left y
    y[2] = w * (x[0] + x[2] / 2) # bottom right x
    y[3] = h * (x[1] + x[3] / 2) # bottom right y
    return y



import pandas as pd
path = 'manholecover/images/'
df = pd.read_csv('manholecover/output.csv')



names = ['Light Fixture', 'Manhole Cover']
n_words = [10]
bbox_expansion_pcts = [1]
loop_closure_certainty = 0.9

for bbox_expansion_pct in bbox_expansion_pcts:
    for n in n_words:

        codebook = np.load(f'visual_words_{n}_surf.npy')
        ir = InstanceRecognizer(bbox_expansion_pct=bbox_expansion_pct, loop_closure_certainty=loop_closure_certainty, codebook=codebook, hessian_threshold=500)

        images = []
        bboxs = []
        for i, row in df.iterrows():
            if row.image in [2127, 862, 2376, 3366, 2394, 3355, '1_1', '1_2', '2_1', '2_2', '3_1', '3_2', ]:
                img_path = path + str(row.image) + '.png'
                
                img = cv2.imread(img_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                det = np.array([row.x, row.y, row.w, row.h])
                bbox = xywhn2xyxy(det)

                # Draw rectangle on image
                x1, y1, x2, y2 = bbox
                x_exp = bbox_expansion_pct * (x2-x1)
                y_exp = bbox_expansion_pct * (y2-y1)
                mask = ir._create_mask(img, bbox)
                kps, des = ir.surf.detectAndCompute(img, mask)
                cv2.drawKeypoints(img, kps, img)
                cv2.rectangle(img, (int(x1 - x_exp), int(y1 - y_exp)), (int(x2 + x_exp), int(y2 + y_exp)), (255), thickness=2)
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255), thickness=2)
                #cv2.imwrite(f'report_plots/{row.image}.png', img)

                #bbox = [int(x) for x in bbox]
                #patch  = [int(bbox[0] - x_exp), int(bbox[1] - y_exp), int(bbox[2] + x_exp), int(bbox[3] + y_exp)]
                #cv2.rectangle(img, (patch[0], patch[1]),(patch[2], patch[3]), (255), thickness=-1)
                #cv2.rectangle(img, (patch[0], patch[1]), (patch[2], bbox[1]), (255), thickness=2)
                #cv2.rectangle(img, (patch[0], bbox[1]), (bbox[0], patch[3]), (255), thickness=2)
                #cv2.rectangle(img, (bbox[0], bbox[3]), (patch[2], patch[3]), (255), thickness=2)
                #cv2.rectangle(img, (bbox[2], bbox[1]), (patch[2], bbox[3]), (255), thickness=2)


                #cv2.imshow(str(row.image), img)
                #cv2.waitKey()
                #cv2.destroyAllWindows() 

                images.append(img)
                bboxs.append(bbox)
                #obj_name = names[row.category]
                #ir.loop_closure(img_gray, bbox, obj_name, frame=row.image)
        #print(ir.loop_closures.values())
        obj_name = names[row.category]
        similarities = ir.get_similarities(images, bboxs, obj_name)

        np.savetxt(f'report_plots/ir_cm_manhole_{n}_{bbox_expansion_pct}.csv', similarities, delimiter=",", fmt='%.2g')
        print(similarities)

#print(ir.loop_closures.values())