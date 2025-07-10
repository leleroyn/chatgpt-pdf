import os

from st_pages import show_pages, Page, add_page_title


def main():
    show_pages(
        [
            Page("pages/ExtractSeal.py", "提取图片中的印章", "📕"),
            Page("pages/OcrSeal.py", "印章提取(Paddle)", "📕"),
            Page("pages/OcrImage.py", "图片文字提取", "🔍"),
            Page("pages/OcrPdf.py", "PDF文字提取", "👓"),
            Page("pages/UploadFileToDfs.py", "上传文件到DFS服务器", "📤"),
            Page("pages/CompressPdf.py", "PDF压缩", "⚡"),
            Page("pages/OcrIdcardLLM.py", "身份证信息提取(OCR+LLM)", "🐋"),
            Page("pages/OcrBusinessLLM.py", "营业执照信息提取(OCR+LLM)", "🐋")

        ]
    )

    add_page_title()


if __name__ == '__main__':
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()
