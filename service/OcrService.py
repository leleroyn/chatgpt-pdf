import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR


class OcrService:
    def __init__(self):
        self.rapid_ocr = RapidOCR()

    def ocr(self, img_bits):
        arr = np.frombuffer(img_bits, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        B_channel, G_channel, R_channel = cv2.split(image)
        res, elapse = self.rapid_ocr(R_channel)
        result = []
        for i in range(len(res)):
            item = []
            value = res[i]
            item.append(value[1])
            item.append(value[2])
            result.append(item)

        return result
