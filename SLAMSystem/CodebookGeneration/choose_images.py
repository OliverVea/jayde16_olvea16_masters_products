import cv2
import numpy as np

video_file = '../videos/downtown_overca!st_02_27_walk_2.avi'

cap = cv2.VideoCapture(video_file)
    
i = 0
while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        break
    
    cv2.imshow('Bike Video', frame)
    key = cv2.waitKey(0)

    if key == ord('s'):
        filename = 'images/frame_'+ f'{i}'.zfill(5) + '.png'
        cv2.imwrite(filename, frame)
    
    i += 1

cap.release()