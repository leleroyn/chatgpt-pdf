import os

from st_pages import show_pages, Page, add_page_title


def main():
    show_pages(
        [
            # Page("pages/Chat.py", "智能对话体验", "🏠"),
            Page("pages/StreamChat.py", "智能对话体验", "🏠"),
            Page("pages/UpdateModel.py", "更新知识库", "📚"),
            Page("pages/ExtractSeal.py", "提取图片中的印章", "📕"),
            Page("pages/OcrImage.py", "图片文字提取", "🔍"),
            Page("pages/OcrPdf.py", "PDF文字提取", "👓"),
            Page("pages/UploadFileToDfs.py", "上传文件到DFS服务器", "📤")
        ]
    )

    add_page_title()


if __name__ == '__main__':
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    main()
