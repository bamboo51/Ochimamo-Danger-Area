import cv2
import numpy as np

class ImageProcessor:
    @staticmethod
    def detect_danger_zones(cv_img):
        """
        画像内の赤色の領域を「危険区域」として検出し、その部分を白で示したマスク画像を返す。
        """
        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        lower1, upper1 = np.array([0, 100, 100]), np.array([10, 255, 255])
        lower2, upper2 = np.array([160, 100, 100]), np.array([179, 255, 255])
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    
    @staticmethod
    def detect_building_mask(cv_img):
        """
        画像内の建物を検出し、その部分を白で示したマスク画像を返す。
        """
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        kernel = np.ones((15, 15), np.uint8)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        mask = np.zeros_like(gray)
        if contours:
            c = max(contours, key=cv2.contourArea)
            cv2.drawContours(mask, [c], -1, 255, thickness=-1)
        return mask