from st_pages import show_pages, Page, add_page_title


def main():
    show_pages(
        [
            # Page("pages/Chat.py", "智能对话体验", "🏠"),
            Page("pages/StreamChat.py", "智能对话体验", "🏠"),
            Page("pages/UpdateModel.py", "更新知识库", ":books:")
        ]
    )

    add_page_title()


if __name__ == '__main__':
    main()
