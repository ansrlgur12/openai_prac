import base64
import requests
import os
from PIL import Image, ImageEnhance
from io import BytesIO

# OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image from URL
def encode_image_from_url(image_url):
    response = requests.get(image_url)
    return base64.b64encode(response.content).decode('utf-8')

# URL of your image
image_url = "https://postfiles.pstatic.net/MjAyNDEwMDhfMjkg/MDAxNzI4MzkwNzc2MjM4.xLz4x9M7CWwO4XdsKvZEBVvCtc6qGb34B0X60-DPnCwg.ggwQyezAlsJg3DQPZbzTckyvrX6d2h34aB3acgnbPLUg.PNG/%EB%B0%B9%EC%9A%B4%EA%B4%91%EC%9E%A5%EB%8F%84%EC%8B%9C%EC%9E%AC%EC%83%9D_%EB%89%B4%EB%94%9C%EC%82%AC%EC%97%85.png?type=w966"

# Getting the base64 string
base64_image = encode_image_from_url(image_url)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "이 이미지는 정부 지원사업에 관한 정보를 담고 있습니다. 다음 사항들에 대해 자세히 설명해주세요:\n1. 총 사업비는 얼마이며, 어떤 항목들로 구성되어 있나요?\n2. 각 지원 항목별 금액은 얼마인가요? (예: 국비, 도비, 시비 등)\n3. 이미지에 나와 있는 모든 금액 정보를 나열해주세요.\n\n각 항목에 대해 구체적인 숫자와 정보를 포함하여 답변해주세요."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 500
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())

# Function to enhance the image
def enhance_image(image_url, scale_factor=2, contrast_factor=1.5, sharpness_factor=1.5):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # 이미지 크기 증가
    new_size = (img.width * scale_factor, img.height * scale_factor)
    img_resized = img.resize(new_size, Image.LANCZOS)
    
    # 대비 향상
    enhancer = ImageEnhance.Contrast(img_resized)
    img_contrast = enhancer.enhance(contrast_factor)
    
    # 선명도 향상
    enhancer = ImageEnhance.Sharpness(img_contrast)
    img_sharp = enhancer.enhance(sharpness_factor)
    
    # 처리된 이미지를 바이트 스트림으로 변환
    buffered = BytesIO()
    img_sharp.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# 기존의 encode_image_from_url 함수 대신 이 함수를 사용
base64_image = enhance_image(image_url)