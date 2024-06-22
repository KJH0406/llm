import streamlit as st
import time

# 페이지 인터페이스 설정
st.title("RAG")

# 메시지 히스토리 관리
if "messages" not in st.session_state: # 세션에 메시지가 없을 때만 새로운 메시지 저장 배열 생성, 만약 이미 가지고 있다면 기존 메시지 세션에 계속해서 저장됨
    st.session_state["messages"] = [] # 세션에 메시지 저장 배열 생성

# 메세지 생성
def send_message(message, role, save=True):
    # 메시지 히스토리 배열에 저장되어 있는 메시지는 배열에 추가하지 않고 표시만 수행
    with st.chat_message(role):
        st.write(message)
    # 메시지 히스토리 배열에 저장되지 않은 메시지만 새롭게 배열에 추가
    if save:
        st.session_state["messages"].append({"message":message, "role": role}) # 메시지 저장 배열에 생성된 메시지와 역할 저장

# 메시지 표시
for message in st.session_state["messages"]:
    # 메시지 히스토리 배열안에 담긴 메시지들은 이미 생성된 메시지임, 따라서 svae=False를 인자로 전달하여 중복 저장되지 않도록 설정
    send_message(message["message"], message["role"], save=False)
    
# 메시지 입력
message = st.chat_input("Send a message") 

# 메시지 입력 완료 시 메세지 생성 함수 실행
if message:
    send_message(message, "humman")
    time.sleep(2)
    send_message("메세지를 확인하였습니다.", "ai")