import io
from base64 import b64decode
from time import time

import cv2
import streamlit as st

from service import *
from service.IPService import IPService


def main():
    load_dotenv()
    llm = os.getenv("LLM_VERSION")
    st.set_page_config(page_title=" 发票信息提取", layout="wide", menu_items={})
    st.subheader(f"🐋发票信息提取(OCR+{llm})")
    uploaded_file = st.file_uploader("上传发票影像", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            st.image(image)
        with columns[1]:
            with st.spinner("Please waiting..."):
                paddle_ocr = PaddleOcrService()
                ips_service = IPService()
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='PNG')
                byte_data = byte_stream.getvalue()
                start = time()
                results = ips_service.invoice_preprocess(byte_data, tool=(0.8, True, False))
                if not results:
                    st.info("没有检测到任何发票.")
                    return
                end = time()
                elapsed1 = end - start
                start = time()
                ocr_result = []
                for res in results:
                    st.info(f"检测到发票，类型:***{ips_service.convert_invoice_type(res['invoice_type'])}*** | 置信值:{res['confidence']}")
                    image_bytes = b64decode(res["corp_image_base64"])
                    image_stream = io.BytesIO(image_bytes)
                    st.image(image_stream)
                    rec_text = paddle_ocr.ocr_text(image_stream.getvalue())
                    ocr_result.append(rec_text)
                ocr_text = "\\n".join(ocr_result)
                st.write(ocr_text)
                end = time()
                elapsed2 = end - start
                st.divider()
                start = time()
                oneApiService = OneApiService(llm)
                res = oneApiService.ocr_invoice_llm(ocr_text)
                end = time()
                elapsed3 = end - start
                st.write(res)
                st.info(f"检测花费：***{elapsed1}***s | OCR花费：***{elapsed2}***s | 提取花费：***{elapsed3}***s")


if __name__ == '__main__':
    main()
