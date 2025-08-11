import PIL.Image
import cv2
import numpy as np
from PIL import Image


def toRGB(image):
    new_image = image.copy()
    if new_image.ndim == 2:
        pass
    elif new_image.shape[2] == 3:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    return Image.fromarray(new_image)


def create_centered_image(image, background_size=(640, 640)):
    """
    创建白板并将指定图片居中放置

    参数:
        image: PIL.Image对象（直接传入图像对象，而非文件路径）
        background_size: 白板尺寸，必须为元组 (宽, 高)

    返回:
        PIL.Image对象
    """
    try:
        # 确保background_size是元组
        if not isinstance(background_size, tuple):
            background_size = tuple(background_size)  # 转换为元组

        # 创建纯白背景
        white_board = Image.new('RGB', background_size, (255, 255, 255))

        if image:
            # 计算居中位置
            x = (background_size[0] - image.width) // 2
            y = (background_size[1] - image.height) // 2

            # 将图片粘贴到白板中心
            white_board.paste(image, (x, y))

        return white_board

    except Exception as e:
        print(f"图片处理错误: {e}")
        return Image.new('RGB', background_size, (255, 255, 255))  # 返回空白图像作为降级处理


def resize_image_if_large(
        img: Image.Image,
        max_size: tuple[int, int] = (320, 320),
        resample=Image.Resampling.LANCZOS
) -> Image.Image:
    """
    如果图片尺寸大于指定尺寸，按比例缩放至该尺寸
    否则返回原图

    参数:
        img: 输入的PIL.Image对象
        max_size: 最大尺寸 (宽度, 高度)，默认320×320
        resample: 缩放算法，默认LANCZOS（高质量）

    返回:
        处理后的PIL.Image对象
    """
    width, height = img.size
    max_width, max_height = max_size

    # 如果图片尺寸已经小于等于目标尺寸，直接返回
    if width <= max_width and height <= max_height:
        return img.copy()

    # 计算保持宽高比的缩放比例
    ratio = min(max_width / width, max_height / height)

    # 计算新尺寸
    new_width = int(width * ratio)
    new_height = int(height * ratio)

    # 应用缩放
    return img.resize((new_width, new_height), resample=resample)

class ExtractSealService(object):
    def __init__(self, img_bits):
        self.img_bits = img_bits

    def pick_seal_image(self):
        """
        红章的提取出来生成图片（只能提取出黑白颜色底的红色印章）
        """
        arr = np.frombuffer(self.img_bits, dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        img_w = 1024 if image.shape[1] > 1024 else image.shape[1]
        image = cv2.resize(image, (img_w, int(img_w * image.shape[0] / image.shape[1])),
                           interpolation=cv2.INTER_AREA if img_w > 1024 else cv2.INTER_CUBIC)
        img_png = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        hue_image = cv2.cvtColor(img_png, cv2.COLOR_BGR2HSV)

        img_real = None
        mask_ranges = [[np.array([0, 43, 46]), np.array([10, 255, 255])]
            , [np.array([156, 43, 46]), np.array([180, 255, 255])]]
        for img_range in mask_ranges:
            th = cv2.inRange(hue_image, img_range[0], img_range[1])
            element = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            th = cv2.dilate(th, element)
            index1 = th == 255
            mask = np.zeros(img_png.shape, np.uint8)
            mask[:, :, :] = (255, 255, 255, 0)
            mask[index1] = img_png[index1]
            if img_real is None:
                img_real = mask
            else:
                img_real = cv2.add(img_real, mask)

        white_px = np.asarray([255, 255, 255, 255])
        (row, col, _) = img_real.shape
        for r in range(row):
            for c in range(col):
                px = img_real[r][c]
                if all(px == white_px):
                    img_real[r][c] = img_png[r][c]

        # 扩充图片防止截取部分
        img4png = cv2.copyMakeBorder(img_real, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
        img5png = cv2.copyMakeBorder(image, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
        img2gray = cv2.cvtColor(img4png, cv2.COLOR_RGBA2GRAY)
        retval, gray_first = cv2.threshold(img2gray, 253, 255, cv2.THRESH_BINARY_INV)

        # 形态学去噪，cv2.MORPH_OPEN先腐蚀再膨胀，cv2.MORPH_CLOSE先膨胀再腐蚀
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        img_real = cv2.morphologyEx(gray_first, cv2.MORPH_OPEN, kernel, iterations=1)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (100, 100))
        img_real = cv2.morphologyEx(img_real, cv2.MORPH_CLOSE, kernel, iterations=1)

        c_canny_img = cv2.Canny(img_real, 10, 10)

        contours, hierarchy = cv2.findContours(c_canny_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt_img = cv2.drawContours(img5png.copy(), contours, -1, (0, 255, 0), 5)
        areas = []
        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            ars = [area, i]
            areas.append(ars)
        areas = sorted(areas, reverse=True)
        print(areas)
        stamps = []
        for item in areas[:4]:
            max_ares = item
            print(item)
            x, y, w, h = cv2.boundingRect(contours[max_ares[1]])
            x = x - 10
            y = y - 10
            w = w + 20
            h = h + 20
            temp = img5png[y:(y + h), x:(x + w)]
            print(temp.shape)
            if temp.shape[0] < temp.shape[1]:
                zh = int((temp.shape[1] - temp.shape[0]) / 2)
                temp = cv2.copyMakeBorder(temp, zh, zh, 0, 0, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
            else:
                zh = int((temp.shape[0] - temp.shape[1]) / 2)
                temp = cv2.copyMakeBorder(temp, 0, 0, zh, zh, cv2.BORDER_CONSTANT, value=[255, 255, 255, 0])
            dst = cv2.resize(temp, (300, 300), interpolation=cv2.INTER_AREA if x > 300 or y > 300 else cv2.INTER_CUBIC)
            stamps.append(dst)
        all_stamp = cv2.hconcat(stamps)
        return toRGB(cnt_img), None if all_stamp is None else toRGB(all_stamp)
