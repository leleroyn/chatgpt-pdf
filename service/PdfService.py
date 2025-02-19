# coding:utf-8

import cv2
import fitz
import numpy as np


def pic_to_pdf(images):
    doc = fitz.open()
    for img in images:
        img_doc = fitz.open("jpg", img)
        pdf_bytes = img_doc.convert_to_pdf()
        img_pdf = fitz.open("pdf", pdf_bytes)
        doc.insert_pdf(img_pdf)

    return doc.write()


def pdf_to_pic(pdf, ratio=50):
    doc = fitz.open("pdf", pdf)
    fitz.paper_size("a4")
    pages_count = doc.page_count
    pic_list = []

    for pg in range(pages_count):
        page = doc[pg]
        zoom_x = 1.33333333
        zoom_y = 1.33333333
        mat = fitz.Matrix(zoom_x, zoom_y)
        pm = page.get_pixmap(matrix=mat, dpi=None, colorspace='rgb', alpha=False)
        img_bits = pm.tobytes()
        np_array = np.frombuffer(img_bits, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        resize_w = 1024 if image.shape[1] > 1024 else image.shape[1]
        dsize = (resize_w, int(resize_w * image.shape[0] / image.shape[1]))
        image = cv2.resize(image, dsize=dsize, fx=1, fy=1, interpolation=cv2.INTER_LINEAR)
        params = [cv2.IMWRITE_JPEG_QUALITY, ratio]  # ratio:0~100
        image = cv2.imencode(".jpg", image, params)[1]
        image = (np.array(image)).tobytes()
        pic_list.append(image)
    return pic_list
