from io import BytesIO
from math import fabs, sin, radians, cos

import cv2
import fitz
import numpy as np
from PIL import ImageOps, Image
from rapid_orientation import RapidOrientation
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


def rotate_bound(image, angle):
    """
     . 旋转图片
     . @param image    opencv读取后的图像
     . @param angle    (逆)旋转角度
    """

    h, w = image.shape[:2]  # 返回(高,宽,色彩通道数),此处取前两个值返回
    newW = int(h * fabs(sin(radians(angle))) + w * fabs(cos(radians(angle))))
    newH = int(w * fabs(sin(radians(angle))) + h * fabs(cos(radians(angle))))
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1)
    M[0, 2] += (newW - w) / 2
    M[1, 2] += (newH - h) / 2
    return cv2.warpAffine(image, M, (newW, newH), borderValue=(255, 255, 255))


def orientation(image_cv):
    """
    对含有文字信息的文档图像进行旋转
    :param image_cv: cv 图像
    :return: 处理完的正常方向图像
    """
    orientation_engine = RapidOrientation()
    orientation_res, elapse = orientation_engine(image_cv)
    print(orientation_res)
    angle = int(orientation_res)
    if angle > 0:
        return rotate_bound(image_cv, angle)
    else:
        return image_cv


class OcrService:
    def __init__(self):
        self.rapid_ocr = RapidOCR(use_cls=False)

    def detect_from_image_path(self, image_path):
        image = Image.open(image_path)
        result = self.detect_from_image(image)
        return result

    def detect_from_image(self, image):
        """
        识别图像文本
        :param image:  pil 图像
        :return:
        """
        image = image.convert('RGB')
        # image = rotate_image_by_exif(image)
        image = pil2cv(image)
        # img_w = 1024 if image.shape[1] > 1024 else image.shape[1]
        # image = cv2.resize(image, (img_w, int(img_w * image.shape[0] / image.shape[1])),
        #                   interpolation=cv2.INTER_AREA)
        image = orientation(image)
        res, elapse = self.rapid_ocr(image)
        result = []
        if res is not None:
            for i in range(len(res)):
                result.append(res[i][1])
        return result

    def detect_from_pdf_path(self, pdf_bits):
        pdf_text = {}
        pdf_doc = fitz.open("pdf", pdf_bits)
        pages = pdf_doc.pages()
        i = 0
        for page in pages:
            zoom_x = 1.33333333
            zoom_y = 1.33333333
            mat = fitz.Matrix(zoom_x, zoom_y)
            pix = page.get_pixmap(matrix=mat, dpi=None, colorspace='rgb', alpha=False)
            img_bits = pix.tobytes()
            img = Image.open(BytesIO(img_bits))
            result = self.detect_from_image(img)
            pdf_text[i] = (img, result)
            i = i + 1
        return pdf_text
