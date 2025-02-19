from openai import OpenAI

class OneApiService:
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = OpenAI(
            api_key="sk-j6Bp6iYqcY9gBZLKD5B4C2E133F54d83961e10548c9e363a",
            base_url="http://192.168.2.228:3000/v1"
        )

    def  ocr_idcard_deepseek(self,question):


        prompt = """
        以下内容可能来源于一张中国大陆的身份证图片的OCR处理文本，请先整理文件内容，然后判断是否是身份证的完整信息，
        如果是返回JSON格式如下：{"code":200,"name":"姓名","sex":"性别","nation":"民族","birthday":"出生日期","address":"居住地址","issue":"签发机构","expireDate":"证件有效期"}， 
        如果不是返回JSON格式如下：{"code":500,"message":"原因"}，请不要返回任何多余的内容，也不需要带样式！
        待处理内容如下：\n          
        """

        content= prompt + question
        print(content)

        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content}
            ],
        )
        print(chat_completion)
        return chat_completion.choices[0].message.content


    def  ocr_business_deepseek(self,question):
        prompt = """
        以下内容可能来源于一张中国大陆的企业营业执照图片的OCR处理文本，请先整理文件内容，然后判断是否是营业执照的完整信息，
        如果是返回JSON格式如下：{"code":200,"name":"企业名称","orgCode":"统一社会信用代码","businessType":"企业类型","person":"法定代表人","address":"住所","capital":"注册金额(单位：万元)","createDate":"成立日期","period":"营业期限(若无返回空)","business":"经营范围"} ，
        如果不是返回JSON格式如下：{"code":500,"message":"原因"}，请不要返回任何多余的内容，也不需要带样式！
        待处理内容如下：\n          
        """

        content= prompt + question
        print(content)

        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": content}
            ],
        )
        print(chat_completion)
        return chat_completion.choices[0].message.content