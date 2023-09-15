import io

import streamlit as st

from service import ExtractSealService


def main():
    st.set_page_config(page_title="提取红色印章图片", layout="wide", menu_items={})
    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
        font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("📕提取红色印章图片")
    uploaded_file = st.file_uploader("上传文件", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        extract_seal = ExtractSealService(uploaded_file.getbuffer())
        cnt_img, extr_img = extract_seal.pick_seal_image()
        with columns[0]:
            st.image(cnt_img)
        with columns[1]:
            if extr_img is None:
                st.warning("没有识别到红色区域!")
            else:
                st.image(extr_img)
                byte_stream = io.BytesIO()
                # 将图像保存到字节流对象中
                extr_img.save(byte_stream, format='JPEG')
                # 获取字节数据
                byte_data = byte_stream.getvalue()
                st.download_button("下载", byte_data,file_name=uploaded_file.name)


if __name__ == '__main__':
    main()
