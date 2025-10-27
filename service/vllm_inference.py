import os
import re
import time
from typing import Optional

import requests
from openai import OpenAI

def image_inference_with_vllm(
        prompt,
        images=None,
        temperature=0.7,
        top_p=0.9,
        max_completion_tokens=2000,
        model_name='qwen3vl',
):
    """
    Call a vision-language model with optional images and a prompt.
    
    Args:
        prompt (str): The user prompt to send to the VLM
        images (list, optional): List of PIL images or single PIL image. Defaults to None.
        temperature (float): Controls randomness (0.0 to 1.0)
        top_p (float): Controls diversity via nucleus sampling (0.0 to 1.0)
        max_completion_tokens (int): Maximum number of tokens to generate
        model_name (str): Specific model to use
        
    Returns:
        str: The response from the VLM or None if there was an error
    """
    client = OpenAI(api_key="{}".format(os.getenv("OPENAI_API_KEY")), base_url=os.getenv("OPENAI_BASE_URL"))
    messages = []
    
    # 在函数内部标准化 images 参数
    if images is None:
        image_list = []
    elif isinstance(images, (list, tuple)):  # 同时接受列表和元组
        image_list = list(images)
    else:
        image_list = [images]
    
    # Build content based on whether we have images or not
    content = []
    
    # Add image URLs if images are provided
    for image in image_list:
        content.append({
            "type": "image_url",
            "image_url": {"url": PILimage_to_base64(image)},
        })
    
    # Add text prompt with image placeholders if images exist
    if image_list:
        image_placeholders = "<|img|><|imgpad|><|endofimg|>" * len(image_list)
        content.append({"type": "text", "text": f"{image_placeholders}{prompt}"})
    else:
        # No images, just text prompt
        content.append({"type": "text", "text": prompt})
    
    messages.append({
        "role": "user",
        "content": content
    })
    
    try:
        start_time = time.time()  # Start timing
        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            top_p=top_p)
        end_time = time.time()  # End timing
        inference_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        response = response.choices[0].message.content
        print(f"VLM inference completed | total: {inference_time:.1f}ms")
        return response
    except requests.exceptions.RequestException as e:
        print(f"request error: {e}")
        return None


def text_inference_with_llm(
        prompt,
        system_message=None,
        temperature=0.1,
        top_p=0.95,
        max_tokens=2048,
        model_name=r'qwen3vl',
):
    """
    Call a text-based large language model with a prompt.
    
    Args:
        prompt (str): The user prompt to send to the LLM
        system_message (str, optional): System message to set the behavior of the assistant
        temperature (float): Controls randomness (0.0 to 1.0)
        top_p (float): Controls diversity via nucleus sampling (0.0 to 1.0)
        max_tokens (int): Maximum number of tokens to generate
        model_name (str, optional): Specific model to use. If None, uses environment variable or defaults to 'gpt-4'
        
    Returns:
        str: The response from the LLM or None if there was an error
    """
    # Get API configuration from settings
    api_key = os.getenv("OPENAI_API_KEY") or ""
    base_url = os.getenv("OPENAI_BASE_URL")
    default_model = os.getenv("LLM_VERSION")
    
    # Use provided model name or fall back to default
    if model_name is None:
        model_name = default_model
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # Prepare messages
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    
    messages.append({"role": "user", "content": prompt})
    
    # Start timing
    start_time = time.time()
    
    try:
        # Call the LLM
        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        text = response.choices[0].message.content

        # End timing
        end_time = time.time()
        inference_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"LLM text inference completed | total: {inference_time:.1f}ms")

        # Handle case where text might be None
        if text is None:
            return None

        # 先移除空标签 <></>
        text = text.replace('<></>', '')

        # 处理各种可能的思考标签
        patterns = [
            r'<[^>]*?>.*?</[^>]*?>',  # 匹配成对的标签，如 <thinking>...</thinking>
            r'```.*?```',            # 移除代码块
            r'Thought process:.*?(?=\n\n|\Z)'  # 移除 "Thought process:" 后的内容
        ]

        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL)

        return text.strip()
    except Exception as e:
        # End timing for error case
        end_time = time.time()
        inference_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"LLM text inference failed | total: {inference_time:.1f}ms | error: {e}")
        print(f"Error calling LLM: {e}")
        return None