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
    head_col = st.columns(2)
    with head_col[0]:
        uploaded_file = st.file_uploader("上传发票影像", type=["png", "jpg", "bmp"])
    with head_col[1]:
        conf_size = st.slider('置信度', min_value=0.1, max_value=1.0, step=0.1, value=0.8)
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            st.image(image)
        with columns[1]:
            with st.spinner("Please waiting..."):
                ips_service = IPService()
                byte_stream = io.BytesIO()
                image.save(byte_stream, format='PNG')
                byte_data = byte_stream.getvalue()
                start = time()
                results = ips_service.invoice_preprocess(byte_data, return_corp_image=False, return_ocr_text=True, tool=(conf_size, True, True))
                if not results:
                    st.info("没有检测到任何发票.")
                    return
                end = time()
                elapsed1 = end - start
                ocr_result = []
                for res in results:
                    st.info(f"检测到发票，类型:***{ips_service.convert_invoice_type(res['invoice_type'])}*** | 置信值:{res['confidence']}")
                    ocr_result.append(res["ocr_text"])
                ocr_text = "\\n".join(ocr_result)
                st.write(ocr_text)
                st.divider()
                start = time()
                oneApiService = OneApiService(llm)
                res = oneApiService.ocr_invoice_llm(ocr_text)
                end = time()
                elapsed3 = end - start
                st.write(res)
                st.info(f"检测花费：***{elapsed1}***s | 提取花费：***{elapsed3}***s")


if __name__ == '__main__':
    main()
