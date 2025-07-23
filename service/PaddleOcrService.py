import base64
import os

import numpy as np
import requests
from PIL import Image
from dotenv import load_dotenv


class PaddleOcrService:

    # 增强红色饱和度
    def boost_red(self, img, saturation_factor=1.5):
        img = img.convert('RGB')
        # 转换到HSV空间，单独增强饱和度
        hsv_img = img.convert('HSV')
        h, s, v = hsv_img.split()
        s = s.point(lambda x: min(255, x * saturation_factor))  # 红色区域饱和度倍增
        enhanced_img = Image.merge('HSV', (h, s, v)).convert('RGB')
        return enhanced_img

    def replace_black_with_white(self, img, threshold=50):
        """将黑色像素替换为白色（支持JPG/PNG）"""
        arr = np.array(img.convert("RGB"))  # 确保RGB格式
        # 检测黑色像素（三通道同时满足条件）
        black_mask = (arr[:, :, 0] < threshold) & \
                     (arr[:, :, 1] < threshold) & \
                     (arr[:, :, 2] < threshold)
        # 替换为白色
        arr[black_mask] = [255, 255, 255]
        return Image.fromarray(arr)

    def remove_black_to_transparent(self, img, threshold=30):
        """将黑色像素替换为透明（需保存为PNG）"""
        img = img.convert("RGBA")  # 转换为RGBA模式
        arr = np.array(img)
        r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

        # 创建黑色像素掩码（RGB值均小于阈值）
        black_mask = (r < threshold) & (g < threshold) & (b < threshold)

        # 将黑色区域设为透明
        arr[black_mask] = [0, 0, 0, 0]  # RGBA: 最后一个0表示完全透明
        return Image.fromarray(arr)

    def remove_black_pixels(self, img, threshold=30):
        """用相邻像素平均值替换黑色（平滑过渡）"""
        import cv2
        arr = np.array(img.convert("RGB"))
        # 创建黑色像素掩码
        black_mask = np.all(arr < threshold, axis=-1)

        # 使用卷积计算左右像素平均值
        kernel = np.array([0.5, 0, 0.5]).reshape(1, 3)  # 水平方向卷积核
        convolved = cv2.filter2D(arr, -1, kernel, borderType=cv2.BORDER_REPLICATE)

        # 仅替换黑色区域
        result = np.where(black_mask[..., None], convolved, arr)
        return Image.fromarray(result.astype('uint8'))

    def ocr_seal(self, image_bytes, file_type=1):
        load_dotenv()
        API_URL = os.getenv("PADDLE_SEAL_URL")  # 服务URL
        image_data = base64.b64encode(image_bytes).decode("ascii")
        payload = {
            "file": image_data, "fileType": file_type}  # Base64编码的文件内容或者图像URL
        # 调用API
        response = requests.post(API_URL, json=payload)
        # 处理接口返回数据
        assert response.status_code == 200
        result = response.json()["result"]
        try:
            # 导航到目标路径: result -> sealRecResults -> [0] -> prunedResult -> seal_res_list -> [0]
            seal_res_list = result["sealRecResults"][0]["prunedResult"]["seal_res_list"]
            all_rec = []
            if seal_res_list:  # 确保列表不为空
                for seal_data in seal_res_list:
                    rec_texts = seal_data["rec_texts"]
                    rec_scores = seal_data["rec_scores"]
                    print("rec_texts:", rec_texts)
                    print("rec_scores:", rec_scores)
                    all_rec.append((rec_texts, rec_scores))
                return all_rec
            else:
                print("seal_res_list为空")
                return "没有找到印章"

        except KeyError as e:
            print(f"键错误: {e}")
        except IndexError as e:
            print(f"索引错误: {e}")
        return "异常"

    def ocr_text(self, file_bytes, file_type=1):
        """
        ocr图片或者pdf文件
        :param file_bytes: 文件bits
        :param file_type: 1=图片,0=pdf文件
        :return:
        """
        global result_text
        load_dotenv()
        API_URL = os.getenv("PADDLE_OCR_URL")
        file_data = base64.b64encode(file_bytes).decode("ascii")
        payload = {
            "file": file_data, "fileType": file_type}  # Base64编码的文件内容或者图像URL
        # 调用API
        response = requests.post(API_URL, json=payload)
        # 处理接口返回数据
        assert response.status_code == 200
        result = response.json()["result"]
        # 提取rec_texts并组合成一段字符串
        combined_text = ""
        for page in result['ocrResults']:
            combined_text += '\n'.join(page['prunedResult']['rec_texts']) + '\n\n'  # 每页内容之间加两个换行符

        return combined_text



