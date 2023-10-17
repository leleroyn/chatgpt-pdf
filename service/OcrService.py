import cv2
import numpy as np
from PIL import ImageOps, Image

from rapidocr_onnxruntime import RapidOCR


def rotate_image_by_exif(image_pil):
    image_pil = ImageOps.exif_transpose(image_pil)
    return image_pil


def pil2cv(image):
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:
        pass
    elif new_image.shape[2] == 3:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image


class OcrService:
    def __init__(self):
        self.rapid_ocr = RapidOCR()

    def detect(self, image_path):
        image = Image.open(image_path).convert('RGB')
        image = rotate_image_by_exif(image)
        image = pil2cv(image)
        img_w = 1024 if image.shape[1] > 1024 else image.shape[1]
        image = cv2.resize(image, (img_w, int(img_w * image.shape[0] / image.shape[1])),
                           interpolation=cv2.INTER_AREA)
        B_channel, G_channel, R_channel = cv2.split(image)
        res, elapse = self.rapid_ocr(R_channel)
        result = []
        if res is not None:
            for i in range(len(res)):
                result.append(res[i][1])

        return result
