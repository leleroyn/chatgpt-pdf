import requests
import json

class DeepSeekHuaweiService:
    def __init__(self, model_name):
        self.model_name = model_name

    def  ocr_idcard_deepseek(self,question):
        prompt = """
        以下内容可能来源于一张中国大陆的身份证图片的OCR处理文本，请先整理文件内容，然后判断是否是身份证完整信息，
        如果是返回JSON格式如下：{"code":200,"name":"姓名","sex":"性别","nation":"民族","birthday":"出生日期","address":"民住地址","issue":"签发机构","expireDate":"证件有效期"} 
        如果不是返回JSON格式如下：{"code":500,"message":"原因"}，请不要返回任何多余的内容！
        待处理内容如下：\n          
        """

        content= prompt + question
        print(content)

        url = "https://infer-modelarts-cn-southwest-2.modelarts-infer.com/v1/infers/fd53915b-8935-48fe-be70-449d76c0fc87/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer _ypJ14s7iSslGcAdCK7wLLkN9PdNCUp00D3nPHLLk6C8VyQ9pbtznW6ziXeOWPW_ZG0zSzdcxngmpCX_P5_mQA'
        }
        data = {
            "model": self.model_name,
            "max_tokens": 2000,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content}
            ],
            "stream": False,
            "temperature": 1.0
        }


        resp = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

        print(resp.status_code)
        print(resp.text)

        return resp

