from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.storage import LocalFileStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
import streamlit as st


# 페이지 인터페이스 설정
st.title("RAG")


# 파일 업로드 위젯(사이드바) 
with st.sidebar:
    file = st.file_uploader("파일을 업로드 해주세요.", type=["pdf", "txt", "docx", "md"])


# 파일을 읽고 벡터 스토어에 저장한 후 검색 기능을 제공
@st.cache_data(show_spinner="임베딩 처리 중입니다.") # 데이터 캐싱
def embed_file(file):
    # 업로드된 파일 처리
    file_content = file.read() 
    file_path = f"./.cache/files/{file.name}" 
    with open(file_path, "wb") as f: 
        f.write(file_content) 
        cache_dir = LocalFileStore(f"./.cache/embeddings/{file.name}")

        # 텍스트 스플리터 설정
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        # separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        )
        loader = UnstructuredFileLoader(file_path)
        docs = loader.load_and_split(text_splitter=splitter)

        # 임베딩
        embeddings = OpenAIEmbeddings()
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

        # 벡터 스토어 생성 및 검색기 설정
        vectorstore = FAISS.from_documents(docs, cached_embeddings)
        retriever = vectorstore.as_retriever()

        return retriever



# 사용자 또는 AI의 메시지를 세션 상태에 저장
def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})

# 메시지를 생성하여 화면에 표시하고 필요한 경우 세션 상태에 저장
def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)

# 세션 상태에 저장된 모든 메시지를 화면에 표시
def print_messages():
    for message in st.session_state["messages"]:
        send_message(message["message"], message["role"], save=False)

# 문서 리스트 포맷팅
def formatting_docs(docs):
    return "\n\n".join(document.page_content for document in docs)


# 채팅 응답 스트리밍 형식으로 설정
class ChatCallbackHandler(BaseCallbackHandler):

    # 향후 세션 상태에 저장할 메시지 변수
    message = ""

    # LLM 응답 시작 시 실행
    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()

    # LLM 응답 종료 시 실행
    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai") # 세션 상태에 저장

    # 새로운 토큰이 생성될 때마다 실행
    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token # 향후 세션 상태에도 저장하기 위해 내용 작성
        self.message_box.markdown(self.message) # 실시간으로 채팅 박스 내용 작성

# LLM 모델 설정
llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0,

    # 스트리밍 및 콜백 사용
    streaming=True,
    callbacks=[
        ChatCallbackHandler(),
    ],
)

# 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    # 시스템 메시지
    ("system",
    """
    Answer the question using ONLY the following context.
    If you don't know the answer just say you don't know. DON'T make anything up.

    Context: {context}
    
    """), 
    # 사용자 메시지
    ("human", "{question}"), 
])


# 파일 처리 로직
if file:
    # 파일을 임베딩하고 검색기 설정
    retriever = embed_file(file)
    
    # 채팅 시작 메시지 설정
    send_message("업로드한 문서에 대해 무엇이든 물어보세요!", "ai", save=False) # save=False 설정을 통하여 채팅 시작 시에만 생성

    # 세션 상태에 저장된 메시지 표시
    print_messages()

    # 사용자 메시지 입력을 받음
    message = st.chat_input("질문을 입력하세요.")

    # 사용자가 메시지를 입력한 경우 실행
    if message:
        send_message(message, "human")
        
        # 체인 설정
        chain = {
            "context" : retriever | RunnableLambda(formatting_docs), # 검색된 문서 포맷팅
            "question" : RunnablePassthrough() # 사용자 질문을 그대로 전달
        } | prompt | llm

        # 체인 실행 및 응답 생성
        with st.chat_message("ai"):
            response = chain.invoke(message)

else:
    # 파일이 업로드되지 않은 경우
    st.write("파일을 업로드 해주세요.")
    st.session_state["messages"] = [] # 세션 상태의 메시지 초기화