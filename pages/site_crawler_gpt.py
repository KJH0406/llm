import streamlit as st
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer

# 페이지 인터페이스 설정
st.title("Site Crawler")

# 사이드바 위젯 설정
with st.sidebar:
    # 크롤링할 페이지 주소
    url = st.text_input("페이지 주소를 입력해주세요", placeholder="https://example.com")


html2text_transformer = Html2TextTransformer()


if url:
    loader = AsyncChromiumLoader([url])
    docs = loader.load()
    transformed = html2text_transformer.transform_documents(docs)
    st.write(transformed)