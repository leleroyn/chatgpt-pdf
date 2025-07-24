import json

import streamlit as st

from service import *


def main():
    load_dotenv()
    st.set_page_config(page_title="合同信息判定", layout="wide", menu_items={})
    st.subheader(f"🐋合同信息判定(OCR+llm)")
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
                url = os.getenv("DFS_URL")
                files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                r = requests.post(url, files=files)
                data = json.loads(r.text)
                print(data)
                file_dfs_url = data["map"]["privateUrl"]
                args = {'fileUrl': file_dfs_url, 'seal': 1, "question": user_input,
                        'returnOcrText': 1, 'returnLLMThink': 1}
                valid_result = requests.post(os.getenv("CONTRACT_VALID_URL"), json=args)
                valid_data = json.loads(valid_result.text)
                print(valid_data)
                st.info("合同内容")
                st.caption(valid_data.get("data", {}).get("ocrText", ""))

        with columns[1]:
            if button:
                st.info("AI思考过程")
                st.caption(valid_data.get("data", {}).get("think", ""))
                st.info("判定结果")
                st.write(
                    ("✔️" if valid_data.get("data", {}).get("result", "") == 1 else "❎️",
                     valid_data.get("data", {}).get(
                         "reason", "")))


if __name__ == '__main__':
    main()
