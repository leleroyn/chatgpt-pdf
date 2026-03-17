import os
import json
import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv


def main():
    load_dotenv()
    st.set_page_config(page_title="手印检测", layout="wide", menu_items={})
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
           font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("👋 手印检测")

    # 1. 先显示 position 输入框
    position_input = st.text_input(
        "Position 参数",
        placeholder="请输入 position 值",
        key="position_input"
    )

    # 2. 文件上传
    uploaded_file = st.file_uploader("上传图片文件", type=["png", "jpg", "bmp", "jpeg", "pdf"])

    # 3. 配置和 URL
    dfs_url = os.getenv("DFS_URL")
    handprint_url = os.getenv("IPS_HANDPRINT_DETECT", "http://192.168.2.203:8088/ai/handprint/detect")

    # 4. 选完文件后，上传到 DFS 并调用接口
    if uploaded_file is not None:
        # 上传到 DFS
        with st.spinner("正在上传到 DFS 服务器..."):
            files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
            r = requests.post(dfs_url, files=files)

        if r.status_code == 200:
            data = json.loads(r.text)
            file_dfs_url = data["map"]["privateUrl"]
            st.success(f"✅ 文件已上传到 DFS: {file_dfs_url}")

            # 调用接口
            with st.spinner("正在检测手印..."):
                headers = {'Content-Type': 'application/json'}
                payload = {
                    "appId": "IVA",
                    "position": position_input.strip() if position_input else "",
                    "fileUrl": file_dfs_url
                }
                response = requests.post(handprint_url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()             

                # 解析检测结果
                if "data" in result:
                    has_handprint = result["data"].get("hasHandprint", False)
                    result_value = result["data"].get("hasHandprint", False)

                    # 显示检测结果
                    st.markdown("#### 检测结果：")
                    if has_handprint:
                        st.success("🟢 检测到手印")
                    else:
                        st.error("❌ 未检测到手印")
                    

                    # 显示 API 返回结果
                    with st.expander("📊 API 返回结果"):
                        st.json(result)
                    

            elif response.status_code == 400:
                error_msg = response.json().get("message", "")
                st.error(f"❌ 手印检测请求错误：{error_msg}")

            elif response.status_code == 500:
                st.error("❌ 手印检测服务器错误，请稍后重试")

            else:
                st.error(f"❌ 手印检测请求失败 (HTTP {response.status_code})")

        else:
            st.error(f"❌ DFS 上传失败 (HTTP {r.status_code}): {r.text}")

    else:
        st.info("💡 请上传图片文件进行手印检测")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **输入 Position**: 填写 Position 参数
            2. **上传图片**: 点击上方上传按钮，选择图片文件
            3. **支持格式**: PNG, JPG, BMP, JPEG, PDF
            4. **自动处理**: 选完文件后，系统自动上传到 DFS 并调用手印检测接口
            5. **查看结果**: 显示手印检测概率和是否存在手印
            """)


if __name__ == '__main__':
    main()
