import json
from time import time

import streamlit as st

from service import *


def main():
    load_dotenv()
    st.set_page_config(page_title="合同信息判定", layout="wide", menu_items={})
    st.subheader(f"📋合同信息判定(OCR+llm)")
    column_head = st.columns([1, 1, 1,1], gap="medium")
    with column_head[0]:
        uploaded_file = st.file_uploader("上传合同影像", type=["png", "jpg", "bmp", "pdf"])
    with column_head[1]:
        seal_options = st.multiselect(
            "印章筛选",
            ["红色圆章", "灰色圆章"],
            default=["红色圆章", "灰色圆章"],
        )
    with column_head[2]:
        doc_options = st.selectbox(
            "文档类型",
            ["合同", "身份证", "营业执照", "发票"]
        )
    with column_head[3]:
        usecls_options = st.selectbox(
            "启用文本方向检测",
            ["启用", "禁用"]
        ) 
    columns = st.columns(3, gap="medium")
    if uploaded_file is not None:
        # Display uploaded image if it's not a PDF
        if not uploaded_file.name.lower().endswith('.pdf'):
            image = Image.open(uploaded_file)
            # Convert CMYK to RGB if needed
            if image.mode == 'CMYK':
                image = image.convert('RGB')
        
        with columns[0]:
            st.divider()
            user_input = st.text_area(
                label="请根据下面格式对合同内容进行提问",
                placeholder="1.是否存在xxx\n2.是否存在xxx",
                height=150
            )
            button = st.button("开始询问")
            if button:
                if not doc_options:
                    st.error("文档类型不能为空", icon="⚠️")
                    return
                if not user_input.strip():
                    st.error("提问内容不能为空", icon="⚠️")
                    return
                url = os.getenv("DFS_URL")
                files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                r = requests.post(url, files=files)
                data = json.loads(r.text)
                file_dfs_url = data["map"]["privateUrl"]
                select_seal = [1 if color == "红色圆章" else 2 if color == "灰色圆章" else None for color in
                               seal_options]
                select_doc = 1 if doc_options == "合同" else 2 if doc_options == "身份证" else 3 if doc_options == "营业执照" else 4 if doc_options == "发票" else None
                start = time()
                args = {'fileUrl': file_dfs_url, 'seal': select_seal, "question": user_input, "doc": select_doc, "useCls": 1 if usecls_options == "启用" else 0,
                        'returnOcrText': 1, 'returnLLMThink': 1}
                valid_result = requests.post(os.getenv("CONTRACT_VALID_URL"), json=args)
                valid_data = json.loads(valid_result.text)
                print(valid_data)
                if valid_data.get("code") == "99":
                    st.error(valid_data.get("message"), icon="⚠️")
                    return
                st.info("合同内容")
                st.caption(valid_data.get("data", {}).get("ocrText", ""))

        with columns[1]:
            st.divider()
            if button:
                st.info("AI思考过程")
                st.caption(valid_data.get("data", {}).get("think", ""))
        with columns[2]:
            st.divider()
            if button:
                st.info("判定结果")
                st.write(
                    ("✔️" if valid_data.get("data", {}).get("result", "") == 1 else "❌",
                     valid_data.get("data", {}).get(
                         "reason", "")))
                end = time()
                elapsed = end - start
                st.info(f"处理花费时间：***{elapsed}***s")


if __name__ == '__main__':
    main()
