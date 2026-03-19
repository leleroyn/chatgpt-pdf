import json
import os
from time import time

import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv


def main():
    load_dotenv()
    llm = os.getenv("LLM_VERSION")
    st.set_page_config(page_title="发票信息提取", layout="wide", menu_items={})
    st.subheader(f"🧾 发票信息提取 (OCR+{llm})")

    uploaded_file = st.file_uploader("上传发票影像", type=["png", "jpg", "bmp", "jpeg", "pdf"])

    if uploaded_file is not None:
        try:
            # Load the image or PDF
            if uploaded_file.type != "application/pdf":
                # Load the image for display only
                image = Image.open(uploaded_file)

            col1, col2 = st.columns(2)

            # Upload to DFS and get URL
            url = os.getenv("DFS_URL")
            files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
            r = requests.post(url, files=files)
            data = json.loads(r.text)
            file_dfs_url = data["map"]["privateUrl"]

            with col1:
                st.subheader("原始文件")
                with st.expander("显示原始文件"):
                    if uploaded_file.type == "application/pdf":
                        st.write(f"PDF 文件：{uploaded_file.name}")
                        st.markdown(f"[{file_dfs_url}]({file_dfs_url})")
                    else:
                        st.image(image, use_column_width=True)

            with col2:
                st.subheader("检测结果")
                with st.spinner("正在检测发票信息..."):
                    headers = {
                        'Content-Type': 'text/plain'
                    }
                    start = time()
                    # 发送 POST 请求
                    response = requests.post(os.getenv("RESOURCE_INVOICE_OCR_URL"), headers=headers, data=file_dfs_url)
                    inv_result = json.loads(response.text)
                    print(inv_result)

                    end = time()
                    elapsed = end - start

                    # Check if code is "00"
                    if isinstance(inv_result, dict) and inv_result.get("code") == "00":
                        invoice_data = inv_result.get("data", {})

                        st.success(f"✅ 发票识别成功")

                        # Helper function to format boolean values
                        def format_boolean(value, true_str="是", false_str="否", default="N/A"):
                            if value == "N/A":
                                return "N/A"
                            return true_str if str(value).strip().lower() == "true" else false_str

                        # Display invoice information in a clean format
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"**发票类型**: {invoice_data.get('invoiceType', 'N/A')}")
                            st.markdown(f"**发票代码**: {invoice_data.get('invoiceCode', 'N/A')}")
                            st.markdown(f"**发票号码**: {invoice_data.get('invoiceNo', 'N/A')}")
                            st.markdown(f"**开票日期**: {invoice_data.get('invoiceDate', 'N/A')}")
                            st.markdown(f"**校验码**: {invoice_data.get('verifyCode', 'N/A')}")

                        with col2:
                            invoice_amt = invoice_data.get('invoiceAmt')
                            invoice_sum = invoice_data.get('invoiceSum')
                            st.markdown(f"**发票金额**: ¥{invoice_amt if invoice_amt not in [None, 'N/A', ''] else 'N/A'}")
                            st.markdown(f"**发票总金额**: ¥{invoice_sum if invoice_sum not in [None, 'N/A', ''] else 'N/A'}")
                            st.markdown(f"**销售方名称**: {invoice_data.get('salerName', 'N/A')}")
                            st.markdown(f"**购买方名称**: {invoice_data.get('purchaserName', 'N/A')}")

                        with col3:
                            is_deduction = invoice_data.get('isDeduction', 'N/A')
                            has_seal = invoice_data.get('hasInvSeal', 'N/A')
                            st.markdown(f"**是否抵扣联**: {format_boolean(is_deduction)}")
                            st.markdown(f"**是否包含国税局印章**: {format_boolean(has_seal)}")

                        st.divider()

                        # Show raw JSON in another expander
                        with st.expander("🔧 查看原始 JSON 数据"):
                            st.json(inv_result)

                        st.markdown(f"**处理时间**: {elapsed:.2f}s")
                        st.divider()

                    else:
                        # Handle error cases
                        error_message = inv_result.get("message", "识别异常") if isinstance(inv_result,
                                                                                            dict) else "识别异常"
                        st.error(f"❌ 识别异常：{error_message}")

                        # Show additional error details if available
                        if inv_result.get("code"):
                            st.info(f"**错误代码**: {inv_result.get('code')}")

                        # Show raw response for debugging
                        with st.expander("🔍 查看原始响应"):
                            st.json(inv_result)

        except Exception as e:
            st.error(f"处理过程中出现错误：{str(e)}")
            st.info("请确保上传的是有效的发票图像，并检查 API 服务是否正常运行。")
    else:
        st.info("💡 请上传发票图片后提取信息")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传发票**: 点击上方上传按钮，选择发票图片或 PDF
            2. **支持格式**: PNG, JPG, BMP, JPEG, PDF
            3. **操作流程**: 上传发票 → OCR 检测 → 查看结果
            4. **功能特点**: 支持多种发票类型，自动识别金额、日期等信息
            """)


if __name__ == '__main__':
    main()
