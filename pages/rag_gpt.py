import streamlit as st
import time

# 페이지 인터페이스 설정
st.title("RAG")

# 파일 업로드
file = st.file_uploader("파일을 업로드 해주세요.", type=["pdf", "txt", "docx", "md"])

if file:
    st.write(file)