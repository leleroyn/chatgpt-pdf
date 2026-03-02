import json
from time import time
import os

import requests
import streamlit as st
from dotenv import load_dotenv

from service import *


def main():
    load_dotenv()
    llm = os.getenv("LLM_VERSION")
    st.set_page_config(page_title="合同关键信息抽取", layout="wide", menu_items={})
    st.subheader(f"📋 合同关键信息抽取(OCR+{llm})")
    
    uploaded_file = st.file_uploader("上传合同影像", type=["png", "jpg", "bmp", "pdf"])
    
    if uploaded_file is not None:
        st.success(f"✅ 已上传文件: {uploaded_file.name}")
        
        # 配置区域 - 使用 expander 收纳配置选项
        with st.expander("⚙️ 提取配置", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                doc_options = st.selectbox(
                    "文档类型",
                    ["合同", "模板文件", "身份证", "营业执照", "发票"]
                )
                seal_options = st.multiselect(
                    "印章筛选",
                    ["红色圆章", "灰色圆章"],
                    default=["红色圆章", "灰色圆章"],
                )
            with col2:
                app_options = st.selectbox(
                    "应用名称",
                    ["实名验证", "融资材料审核", "建档材料审核"]
                )
                # Map the selected application name to its corresponding appId
                app_id_mapping = {
                    "实名验证": "IVA",
                    "融资材料审核": "FDR",
                    "建档材料审核": "ADR"
                }
                selected_app_id = app_id_mapping[app_options]
            with col3:
                usecls_options = st.selectbox(
                    "启用文本方向检测",
                    ["启用", "禁用"]
                )
        
        # 查询输入区域
        st.markdown("### 🎯 关键信息提取")
        user_input = st.text_area(
            label="请输入要抽取的关键内容",
            placeholder="如姓名,性别，出生日期",
            height=100           
        )
        
        # 执行按钮
        col_left, col_right = st.columns([1, 4])
        with col_left:
            button = st.button("🚀 开始提取", type="primary")
        
        # 结果显示区域
        if button:
            if not doc_options:
                st.error("文档类型不能为空", icon="⚠️")
                return
            if not user_input.strip():
                st.error("抽取的关键内容不能为空", icon="⚠️")
                return
            
            # 处理逻辑
            with st.spinner("🔄 正在处理中..."):
                url = os.getenv("DFS_URL")
                files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                r = requests.post(url, files=files)
                data = json.loads(r.text)
                print(data)
                file_dfs_url = data["map"]["privateUrl"]
                select_seal = [1 if color == "红色圆章" else 2 if color == "灰色圆章" else None for color in
                               seal_options]
                select_doc = 1 if doc_options == "合同" else 2 if doc_options == "身份证" else 3 if doc_options == "营业执照" else 4 if doc_options == "发票" else 5 if doc_options == "模板文件" else None
                print(select_doc)
                args = {'fileUrl': file_dfs_url, 'seal': select_seal, "question": user_input, "doc": select_doc, "useCls": 1 if usecls_options == "启用" else 0,
                        'returnOcrText': 1, 'returnLLMThink': 1, "appId": selected_app_id}
                start = time()
                valid_result = requests.post(os.getenv("CONTRACT_EXTRACT_URL"), json=args)
                valid_data = json.loads(valid_result.text)
                print(valid_data)
                
                if valid_data.get("code") == "99":
                    st.error(valid_data.get("message"), icon="⚠️")
                    return
                
                end = time()
                elapsed = end - start
            
            # 结果展示 
            source_col,result_col = st.columns([1, 1])
            with source_col:

                st.markdown("#### 📄 处理信息")
                with st.expander("📋 合同内容", expanded=False):
                    ocr_text = valid_data.get("data", {}).get("ocrText", "")
                    if ocr_text:
                        st.markdown(f"```\n{ocr_text}\n```")
                    else:
                        st.info("未获取到合同文本")
                
                st.metric("⏱️ 处理时间", f"{elapsed:.2f}s")

            with result_col:  
                st.markdown("### 📊 提取结果")             
                result = valid_data.get("data", {}).get("result", "")
                if result:
                    st.write(result)
                else:
                    st.warning("未提取到相关信息")
    else:
        st.info("💡 请上传合同影像后提取关键信息")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传合同**: 点击上方上传按钮，选择合同文件
            2. **支持格式**: PNG, JPG, BMP, PDF
            3. **配置选项**: 
               - 文档类型：合同/模板文件/身份证/营业执照/发票
               - 印章筛选：红色圆章/灰色圆章
               - 应用名称：实名验证/融资材料审核/建档材料审核
               - 文本方向检测：启用/禁用
            4. **操作流程**: 上传合同 → 配置选项 → 输入关键信息 → 开始提取 → 查看结果
            """)


if __name__ == '__main__':
    main()
