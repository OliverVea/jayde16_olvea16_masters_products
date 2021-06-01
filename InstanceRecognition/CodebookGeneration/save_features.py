import numpy as np
import cv2
import glob

def detect_features(img):
    _, des = surf.detectAndCompute(img,None)
    if des is not None:
        for d in des:
            features.append(d)

features = []
surf = cv2.xfeatures2d.SURF_create(500)
#surf = cv2.SURF_create(500)



'''
video_files = glob.glob('../videos/*.avi')
for video_file in video_files:
    cap = cv2.VideoCapture(video_file)
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret: 
            break

        detect_features(frame)
    
    cap.release()
'''

image_files = glob.glob('images/*.png')

for image_file in image_files:
    img = cv2.imread(image_file)
    detect_features(img)

np.save('surf_features.npy', features)