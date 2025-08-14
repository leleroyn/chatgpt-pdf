import os

from st_pages import show_pages, Page, add_page_title


def main():
    show_pages(
        [
            Page("pages/ExtractSeal.py", "检测图片中的印章", "📕"),
            Page("pages/OcrSeal.py", "印章提取(Paddle)", "📕"),
            Page("pages/OcrImage.py", "图片文字提取(Paddle)", "🚤"),
            Page("pages/OcrPdf.py", "PDF文字提取(Paddle)", "🚤"),
            Page("pages/UploadFileToDfs.py", "上传文件到DFS服务器", "📤"),
            Page("pages/CompressPdf.py", "PDF压缩", "⚡"),
            Page("pages/OcrIdcardLLM.py", "身份证信息提取(OCR+LLM)", "🐋"),
            #Page("pages/OcrIdcardVL.py", "身份证信息提取(QwenVL)⭐️", "🐻"),
            Page("pages/OcrBusinessLLM.py", "营业执照信息提取(OCR+LLM)⭐️", "🐋"),
            #Page("pages/OcrBusinessVL.py", "营业执照信息提取(QwenVL)⭐️", "🐻"),
            Page("pages/OcrInvoiceLLM.py", "发票信息提取(OCR+LLM)⭐️", "🐋"),
            #Page("pages/OcrInvoiceVL.py", "发票信息提取(QwenVL)", "🐻"),
            Page("pages/ContractInfoLLM.py", "合同信息判定(OCR+LLM)", "🐋"),
            Page("pages/ContractInfoExtractLLM.py", "合同关键信息抽取(OCR+LLM)", "🐋"),
        ]
    )

    add_page_title()


if __name__ == '__main__':
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()
