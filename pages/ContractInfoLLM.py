from time import time

import streamlit as st

from service import *


def main():
    load_dotenv()
    llm = os.getenv("LLM_VERSION")
    st.set_page_config(page_title="合同信息判定", layout="wide", menu_items={})
    st.subheader(f"🐋合同信息判定(OCR+{llm})")
    uploaded_file = st.file_uploader("上传合同影像", type=["png", "jpg", "bmp", "pdf"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            user_input = st.text_area(
                label="请根据下面格式对合同内容进行提问",  # 顶部加粗提示
                placeholder="1.是否存在xxx\n2.是否存在xxx",  # 框内灰色提示
                height=150  # 设置输入框高度
            )
            button = st.button("开始询问")
            if button:
                file_bits = uploaded_file.getvalue()
                start = time()
                paddleOcr = PaddleOcrService()
                if uploaded_file.name.lower().endswith(".pdf"):
                    text = paddleOcr.ocr_text(file_bits, 0)
                else:
                    text = paddleOcr.ocr_text(file_bits, 1)
                end = time()
                elapsed = end - start
                st.info("识别完成，共花费 {} seconds".format(elapsed))
                st.caption(text)

        with columns[1]:
            if button:
                start = time()
                oneApiService = OneApiService(llm)
                result = oneApiService.contract_llm(user_input, text)
                end = time()
                elapsed = end - start
                st.info("处理完成，共花费 {} seconds".format(elapsed))
                st.write(result)


if __name__ == '__main__':
    main()
