import fitz 

import google.generativeai as genai

import os
from dotenv import load_dotenv
load_dotenv()


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Gemini Model List
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)

def extract_text_from_pdf(pdf_path):
    # PDF 파일에서 텍스트 추출
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

pdf_path = './test.pdf'

origin_content = extract_text_from_pdf(pdf_path)

model = genai.GenerativeModel('gemini-1.5-pro-latest')

prompt =f"""
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Please make sure to answer in Korean.

Question: "양면 인쇄하려면 어떻게 해야하나요?"
Context: {origin_content}
"""

response = model.generate_content(prompt)

text = response._result.candidates[0].content.parts[0]

print(text)

