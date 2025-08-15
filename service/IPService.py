import base64
import io
import os
from typing import Tuple, List, Dict

import requests
from PIL import Image


class IPService:
    def seal_preprocess(self, image_bytes, return_seal_image: bool = True, return_ocr_text: bool = True,
                        tool: Tuple[float, bool, bool] = (0.5, True, True)) -> List[Dict]:
        API_URL = os.getenv("IPS_SEAL_PREPROCESS")  # 服务URL
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "image_base64": image_data,
            "return_seal_image": return_seal_image,
            "return_ocr_text": return_ocr_text,
            "tool": {"init_confidence": tool[0],
                     "resize": tool[1],
                     "back_ground": tool[2]
                     }
        }
        # 调用API
        response = requests.post(API_URL, json=payload)
        # 处理接口返回数据
        if response.status_code != 200:
            error_msg = f"IPS服务调用失败！状态码：{response.status_code}，响应：{response.text[:500]}"
            raise ConnectionError(error_msg)  # 触发可捕获的异常
        return response.json()

    def invoice_preprocess(self, image_bytes, return_corp_image: bool = True, return_ocr_text: bool = True,
                           tool: Tuple[float, bool, bool] = (0.5, True, False)) -> List[Dict]:
        API_URL = os.getenv("IPS_INVOICE_PREPROCESS")  # 服务URL
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "image_base64": image_data,
            "return_corp_image": return_corp_image,
            "return_ocr_text": return_ocr_text,
            "tool": {"init_confidence": tool[0],
                     "resize": tool[1],
                     "back_ground": tool[2]
                     }
        }
        # 调用API
        response = requests.post(API_URL, json=payload)
        # 处理接口返回数据
        if response.status_code != 200:
            error_msg = f"IPS服务调用失败！状态码：{response.status_code}，响应：{response.text[:500]}"
            raise ConnectionError(error_msg)  # 触发可捕获的异常
        return response.json()

    def idcard_preprocess(self, image_bytes, return_corp_image: bool = True, return_ocr_text: bool = False,
                          tool: Tuple[float, bool, bool] = (0.5, True, False)) -> List[Dict]:
        API_URL = os.getenv("IPS_IDCARD_PREPROCESS")  # 服务URL
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "image_base64": image_data,
            "return_corp_image": return_corp_image,
            "return_ocr_text": return_ocr_text,
            "tool": {"init_confidence": tool[0],
                     "resize": tool[1],
                     "back_ground": tool[2]
                     }
        }
        # 调用API
        response = requests.post(API_URL, json=payload)
        # 处理接口返回数据
        if response.status_code != 200:
            error_msg = f"IPS服务调用失败！状态码：{response.status_code}，响应：{response.text[:500]}"
            raise ConnectionError(error_msg)  # 触发可捕获的异常
        return response.json()

    def convert_seal_type(self, seal_code):
        """
        将印章类型编码转换为中文描述
        :param seal_code: 印章类型编码（整数 1 或 2）
        :return: 对应的中文描述字符串
        """
        seal_type_mapping = {
            1: "圆形,红色",
            2: "圆形,灰色"
        }
        return seal_type_mapping.get(seal_code, "未知类型")

    def convert_invoice_type(self, invoice_code):
        """
        将印章类型编码转换为中文描述
        :param seal_code: 印章类型编码（整数 1 或 2）
        :return: 对应的中文描述字符串
        """
        seal_type_mapping = {
            1: "发票"
        }
        return seal_type_mapping.get(invoice_code, "未知类型")

    def convert_idcard_type(self, idcard_code):
        """
        将印章类型编码转换为中文描述
        :param idcard_code: 印章类型编码（整数 1 或 2）
        :return: 对应的中文描述字符串
        """
        seal_type_mapping = {
            1: "正面",
            2: "背面"
        }
        return seal_type_mapping.get(idcard_code, "未知类型")

    def base64_to_pil(self, base64_str):
        # 1. 去除Base64前缀（如"data:image/png;base64,"）
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]

        # 2. 解码Base64为字节数据
        image_bytes = base64.b64decode(base64_str)

        # 3. 通过BytesIO将字节数据转换为PIL.Image对象
        image = Image.open(io.BytesIO(image_bytes))

        # 4. 可选：确保输出为RGB格式（避免透明通道问题）
        return image.convert("RGB")
