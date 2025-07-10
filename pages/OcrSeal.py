import io

import streamlit as st

from service import *


def main():
    st.set_page_config(page_title="印章提取(Paddle)", layout="wide", menu_items={})
    # 隐藏右边的菜单以及页脚
    hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} p {
        font-size:14px}</style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.subheader("📕印章提取(Paddle)")
    uploaded_file = st.file_uploader("上传文件", type=["png", "jpg", "bmp"])
    columns = st.columns(2)
    if uploaded_file is not None:
        with columns[0]:
            image = Image.open(uploaded_file)
            orientation_image = orientation(pil2cv(image))
            st.image(toRGB(orientation_image))
        with columns[1]:
            paddle_ocr = PaddleOcrService()

            fin_img = paddle_ocr.replace_black_with_white(paddle_ocr.boost_red(image, saturation_factor=2.8),
                                                              threshold=50)
            #fin_img = paddle_ocr.boost_red(paddle_ocr.replace_black_with_white(image, threshold=50), saturation_factor=2.8)

            byte_stream = io.BytesIO()
            # 将图像保存到字节流对象中
            fin_img.save(byte_stream, format='PNG')
            # 获取字节数据
            byte_data = byte_stream.getvalue()
            result = paddle_ocr.ocr_seal(byte_data)
            st.write(result)
            st.download_button("下载", byte_data, file_name=uploaded_file.name)


if __name__ == '__main__':
    main()
