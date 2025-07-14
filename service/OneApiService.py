import base64

from openai import OpenAI


class OneApiService:
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = OpenAI(
            api_key="sk-j6Bp6iYqcY9gBZLKD5B4C2E133F54d83961e10548c9e363a",
            base_url="http://192.168.2.228:3000/v1"
        )

    def ocr_idcard_llm(self, question):
        prompt = f'''
        # 以下内容可能来源于一张中国大陆的身份证图片的OCR处理文本:
        {question}
        # 你要处理的问题：
        - 请先整理文件内容，然后判断是否是身份证，
        - 如果是返回json：{{"code":200,"name":"姓名","sex":"性别","nation":"民族","birthday":"出生日期","idNo":"公民身份号码","address":"居住地址","issue":"签发机构(若无返回空)","expireDate":"证件有效期(若无返回空)"}}。
        - 如果不是返回json：{{"code":500,"message":"原因"}}。
        # 在回答时，请注意以下几点：       
        - 切记不要返回任何多余的内容！
        - 结果一定要用json返回，不需要makedown样式 。
        <no_think>
        '''
        print(prompt)

        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        print(chat_completion)
        return chat_completion.choices[0].message.content

    def ocr_business_llm(self, question):
        prompt = f'''
        # 以下内容可能来源于一张中国大陆的企业营业执照图片的OCR处理文本:
        {question}
        # 你要处理的问题：
        - 请先整理文件内容，然后判断是否是营业执照。
        - 如果是返回json：{{"code":200,"name":"企业名称","orgCode":"统一社会信用代码","businessType":"企业类型","person":"法定代表人","address":"住所","capital":"注册金额(单位：万元)","createDate":"成立日期","period":"营业期限(若无返回空)","business":"经营范围"}}。
        - 如果不是返回json：{{"code":500,"message":"原因"}}。
        # 在回答时，请注意以下几点：        
        - 切记不要返回任何多余的内容！
        - 结果一定要用json返回，不需要makedown样式 。
         <no_think>            
        '''

        print(prompt)

        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        print(chat_completion)
        return chat_completion.choices[0].message.content

    def ocr_idcard_vl(self, image_bytes):
        prompt = '''
        你是一个身份证识别专用模型，请严格按以下规则处理：
        1.仅返回JSON格式数据，绝对不要包含任何解释、额外文字或Markdown代码块
        2.禁止修改原始识别结果，即使不完整
        3.从图片中提取中华人民共和国居民身份证信息，按字段输出：
        - name(姓名) | gender(性别) | ethnicity(民族，注意：按原文直接返回!)
        - birth_date(出生,YYYY-MM-DD格式) | address(住址) 
        - id_number(公民身份号码) | issuing_authority(签发机关，若无则空字符串) | valid_period(有效期限,按原文直接返回，若无则空字符串)
        4.状态规则：
        - 成功(code=200)：所有必填项完整且格式正确
        - 失败(code=500)：任一必填项缺失/格式错误，返回msg字段说明具体原因
        5.响应格式唯一性：{ "code": , "name": , "gender": , ... } 或 { "code": , "msg": }
        现在开始识别身份证，输出必须严格遵守：
        {
        "code": 200,
        "name": "",
        "gender": "",
        "ethnicity": "",
        "birth_date": "",
        "address": "",
        "id_number": "",
        "issuing_authority": "",
        "valid_period": ""
        }
        '''
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ], temperature=0
        )
        print(chat_completion)
        return chat_completion.choices[0].message.content

    def ocr_business_vl(self, image_bytes):
        prompt = '''
        你是一个企业营业执照识别专用模型，请严格按以下规则处理：
        1.仅返回JSON格式数据，绝对不要包含任何解释、额外文字或Markdown代码块
        2.禁止修改原始识别结果
        3.从图片中提取中国大陆企业营业执照信息，按字段输出：
          - name(名称) | org_code(社会统一信用代码) | business_type(类型) | person(法定代表人)
          - create_date(成立日期,YYYY-MM-DD格式) | business(经营范围) | address(住所)
          - capital(注册资本) | period(营业期限,若无返回空)
        4.状态规则：
          - 成功(code=200)：所有必填项完整且格式正确
          - 失败(code=500)：任一必填项缺失/格式错误/资本转换失败，返回msg字段说明具体原因
        5.响应格式：
          - 成功：{ "code": 200, "name": "", "org_code": "", ...  } 
          - 失败：{ "code": 500, "msg": "请重新上传更清晰的图片" }  
        '''
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ], temperature=0
        )
        print(chat_completion)
        return chat_completion.choices[0].message.content

    def ocr_invoice_vl(self, image_bytes):
        prompt = '''
        你是一个发票识别专用模型，请严格按以下规则处理：
        1.仅返回JSON格式数据，绝对不要包含任何解释、额外文字或Markdown代码块
        2.禁止修改原始识别结果
        3.从图片中提取中国大陆税务局开具的发票信息，按字段输出：
          - invoice_no(发票号码,必填，为空时直接判定失败) | invoice_code(发票代码,电子发票时可能为空) | invoice_type(发票类型) | verify_code(校验码)
          - invoice_date(开票日期,必填,YYYY-MM-DD格式) | purchaser_name(购货方公司名称) | seller_name(销售方公司名称)
          - invoice_amt(发票金额,必填) | invoice_sum(发票总金额,必填)| invoice_tax(发票税金额,必填)
        4.发票金额,发票总金额,发票税金额的关系
          - 发票总金额 = 发票金额 + 发票税金额
        5.状态规则：         
          - 成功(code=200)：所有必填项完整且格式正确
          - 失败(code=500)：任一必填项缺失/格式错误/资本转换失败，返回msg字段说明具体原因
        6.响应格式：
          - 成功：{ "code": 200, "name": "", "org_code": "", ...  } 
          - 失败：{ "code": 500, "msg": "请重新上传更清晰的图片" }  
        '''
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        chat_completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ], temperature=0
        )
        print(chat_completion)
        return chat_completion.choices[0].message.content
