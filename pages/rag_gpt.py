import streamlit as st
import time

st.title("RAG")


with st.chat_message("human"): # 메시지 컨테이너의 역할을 human으로 설정
    st.write("hello!") # 메시지 컨테이너 안에 텍스트 작성

with st.chat_message("ai"): # 메시지 컨테이너의 역할을 ai로 설정
    st.write("how are you!") # 메시지 컨테이너 안에 텍스트 작성

st.chat_input("Send a message") # 페이지 하단에 채팅을 입력할 수 있는 input 생성
                                # 괄호 안에는 placeholder 작성

 # 컨테이너를 통해 상태를 표시할 수 있음.
with st.status("처리 중...", expanded=True) as status: # expanded 통해서 아래 처리 과정 표시 여부 설정 가능
    time.sleep(2) # time 설정 안하면 무한 로딩
    st.write("파일을 가져오는 중입니다.")
    time.sleep(2) 
    st.write("파일을 임베딩하는 중입니다.")
    time.sleep(2) 
    st.write("파일을 캐싱하는 중입니다.")
    time.sleep(2) 
    status.update(label="완료되었습니다.", state="complete")



