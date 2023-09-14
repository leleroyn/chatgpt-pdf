import cv2
import numpy as np
from PIL import Image


class ExtractSealService(object):
    def __init__(self, img_bits):
        self.img_bits = img_bits

    def cv2pil(self,image):
        new_image = image.copy()
        if new_image.ndim == 2:
            pass
        elif new_image.shape[2] == 3:
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        elif new_image.shape[2] == 4:
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
        new_image = Image.fromarray(new_image)
        return new_image

    # 红章的提取出来生成图片（只能提取出黑白颜色底的红色印章）
    def pick_seal_image(self):

        arr = np.frombuffer(self.img_bits, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        img_w = 768 if image.shape[1] > 768 else image.shape[1]
        image = cv2.resize(image, (img_w, int(img_w * image.shape[0] / image.shape[1])), interpolation=cv2.IMREAD_COLOR)
        img_png = cv2.cvtColor(image.copy(), cv2.COLOR_RGB2RGBA)
        hue_image = cv2.cvtColor(img_png, cv2.COLOR_BGR2HSV)

        img_real = None
        mask_ranges = [[np.array([130, 43, 46]), np.array([180, 255, 255])]
            , [np.array([6, 36, 244]), np.array([9, 255, 255])]]
        for img_range in mask_ranges:
            th = cv2.inRange(hue_image, img_range[0], img_range[1])
            element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            th = cv2.dilate(th, element)
            index1 = th == 255
            mask = np.zeros(img_png.shape, np.uint8)
            mask[:, :, :] = (255, 255, 255, 0)
            mask[index1] = img_png[index1]
            if img_real is None:
                img_real = mask
            else:
                img_real = cv2.add(img_real, mask)

        white_px = np.asarray([255, 255, 255, 255])
        (row, col, _) = img_real.shape
        for r in range(row):
            for c in range(col):
                px = img_real[r][c]
                if all(px == white_px):
                    img_real[r][c] = img_png[r][c]

        # 扩充图片防止截取部分
        img4png = cv2.copyMakeBorder(img_real, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
        img5png = cv2.copyMakeBorder(image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
        img2gray = cv2.cvtColor(img4png, cv2.COLOR_RGBA2GRAY)
        retval, gray_first = cv2.threshold(img2gray, 253, 255, cv2.THRESH_BINARY_INV)

        element = cv2.getStructuringElement(cv2.MORPH_RECT, (22, 22))
        img6 = cv2.dilate(gray_first, element)

        c_canny_img = cv2.Canny(img6, 10, 10)

        contours, hierarchy = cv2.findContours(c_canny_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        areas = []
        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            ars = [area, i]
            areas.append(ars)
        areas = sorted(areas, reverse=True)
        print(areas)
        stamps = []
        for item in areas[:4]:
            max_ares = item
            print(item)
            x, y, w, h = cv2.boundingRect(contours[max_ares[1]])
            temp = img5png[y:(y + h), x:(x + w)]
            print(temp.shape)
            if temp.shape[0] < temp.shape[1]:
                zh = int((temp.shape[1] - temp.shape[0]) / 2)
                temp = cv2.copyMakeBorder(temp, zh, zh, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
            else:
                zh = int((temp.shape[0] - temp.shape[1]) / 2)
                temp = cv2.copyMakeBorder(temp, 0, 0, zh, zh, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
            dst = cv2.resize(temp, (300, 300))
            stamps.append(dst)
        all_stamp = cv2.hconcat(stamps)
        return self.cv2pil(all_stamp)
