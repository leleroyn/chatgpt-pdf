from io import BytesIO
from math import fabs, sin, radians, cos
import base64
import os
import requests

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


def enhance_text_clarity(pil_image,
                         sharpen_strength=1.8,
                         contrast_factor=1.5,
                         use_unsharp_mask=True,
                         use_contrast=True):
    """
    增强图像中文字的清晰度（支持文档/身份证等场景）

    参数:
        pil_image: PIL.Image对象（支持RGB/L模式）
        sharpen_strength: 锐化强度 (1.0-3.0)，默认为1.8
        contrast_factor: 对比度增强系数 (1.0-3.0)，默认为1.5
        use_unsharp_mask: 启用未锐化掩模算法，默认为True
        use_contrast: 启用对比度增强，默认为True

    返回:
        PIL.Image对象（L模式）
    """
    # 转换为OpenCV格式（自动处理色彩空间）
    if pil_image.mode == 'RGB':
        np_image = np.array(pil_image)
        opencv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = np.array(pil_image)

    # 1. 未锐化掩模技术（核心文字增强）
    if use_unsharp_mask:
        blurred = cv2.GaussianBlur(gray, (0, 0), 3.0)
        unsharp = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        enhanced = unsharp
    else:
        enhanced = gray

    # 2. 对比度增强（强化文字与背景差异）
    if use_contrast:
        enhanced = cv2.convertScaleAbs(enhanced, alpha=contrast_factor, beta=0)

    # 3. 锐化加强（可选：针对小字号文本）
    if sharpen_strength > 1.0:
        kernel = np.array([[0, -1, 0],
                           [-1, 5 * sharpen_strength, -1],
                           [0, -1, 0]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)

    # 4. 二值化优化（增强黑白对比）
    _, binary = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU  # 自动计算最佳阈值
    )

    # 转回PIL格式
    return Image.fromarray(binary, 'L')


class OcrService:
    def __init__(self):
        self.api_url = os.getenv("IPS_OCR_PREPROCESS")
        if not self.api_url:
            raise ValueError("IPS_OCR_PREPROCESS environment variable not set")

    def detect_from_image_path(self, image_path):
        image = Image.open(image_path)
        result = self.detect_from_image(image)
        return result

    def detect_from_image(self, image):
        """
        识别图像文本
        :param image: PIL图像
        :return: 识别结果列表
        """
        # 将PIL图像转换为字节
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # 将图像转换为base64
        image_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        
        # 调用OCR接口
        payload = {
            "image_base64": image_base64,
            "return_ocr_text": True
        }
        
        response = requests.post(self.api_url, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"OCR API调用失败，状态码: {response.status_code}, 响应: {response.text}")
        
        result_data = response.json()
        
        # 解析OCR结果
        if result_data.get("code") == 200 or 'ocr_text' in result_data:
            ocr_text = result_data.get("ocr_text", "")
            # 将文本按行分割并返回
            return [line.strip() for line in ocr_text.split('\n') if line.strip()]
        else:
            error_msg = result_data.get('msg', '未知错误')
            error_details = f"API响应: {result_data}" if not result_data.get('msg') else ""
            raise Exception(f"OCR识别失败: {error_msg}. {error_details}")

    def detect_from_pdf_path(self, pdf_bits):
        """
        处理PDF文件，将其转换为图片后调用OCR接口
        :param pdf_bits: PDF文件的字节数据
        :return: 包含每页识别结果的字典
        """
        pdf_text = {}
        pdf_doc = fitz.open("pdf", pdf_bits)
        total_pages = pdf_doc.page_count
        
        print(f"开始处理PDF，共 {total_pages} 页")
        
        for i in range(total_pages):
            print(f"正在处理第 {i+1}/{total_pages} 页...")
            page = pdf_doc[i]
            zoom_x = 1.33333333
            zoom_y = 1.33333333
            mat = fitz.Matrix(zoom_x, zoom_y)
            pix = page.get_pixmap(matrix=mat, dpi=None, colorspace='rgb', alpha=False)
            img_bits = pix.tobytes()
            img = Image.open(BytesIO(img_bits))
            result = self.detect_from_image(img)
            pdf_text[i] = (img, result)
            print(f"第 {i+1}/{total_pages} 页处理完成，识别到 {len(result)} 个文本块")
        
        pdf_doc.close()
        print(f"PDF处理完成，共处理 {total_pages} 页")
        return pdf_text
