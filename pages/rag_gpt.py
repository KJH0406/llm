from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.prompts import ChatPromptTemplate
import streamlit as st

# 페이지 인터페이스 설정
st.title("RAG")

# 파일 업로드
with st.sidebar:
    file = st.file_uploader("파일을 업로드 해주세요.", type=["pdf", "txt", "docx", "md"]) # 업로드 가능한 파일 확장자 지정

@st.cache_data(show_spinner="임베딩 처리 중입니다.")
def embed_file(file):
    file_content = file.read() # 업로드된 파일의 내용을 읽어서 file_content 변수에 저장
    file_path = f"./.cache/files/{file.name}" # 파일을 저장할 경로 지정
    with open(file_path, "wb") as f: # 파일 경로에서 파일을 열고
        f.write(file_content) # 파일 내용 저장
        cache_dir = LocalFileStore(f"./.cache/embeddings/{file.name}")

        splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
        )

        loader = UnstructuredFileLoader(file_path)
        docs = loader.load_and_split(text_splitter=splitter)
        embeddings = OpenAIEmbeddings()
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
        vectorstore = FAISS.from_documents(docs, cached_embeddings)
        retriever = vectorstore.as_retriever()

        return retriever

# 메시지 생성
def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message) # 마크다운 형식으로 메시지 표현
    
    if save:
        st.session_state["messages"].append({"message": message, "role": role})

# 채팅 기록 표시
def print_messages():
    for message in st.session_state["messages"]:
        send_message(message["message"], message["role"], save=False)

# 프롬프트 템플릿 생성
template = ChatPromptTemplate.from_messages([
    # 시스템 프롬프트 입력
    ("system",
    """
    You are an assistant for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

    Context: {context}
    
    """), 
     # 사용자 질문 입력
    ("human", "{question}"), 
])

# 파일 처리 로직
if file:
    # 임베딩된 파일에서 사용자 질문과 관련된 내용 추출
    retriever = embed_file(file)
    
    # 채팅 시작 메시지 설정(AI)
    send_message("업로드한 문서에 대해 무엇이든 물어보세요!", "ai", save=False) # save=False 설정을 통하여 처음 채팅 시작 시에만 생성

    # 메시지 표시
    print_messages()

    # 질문 입력
    message = st.chat_input("질문을 입력하세요.")

    # 사용자가 메시지 입력 시 실행
    if message:
        send_message(message, "human") # 메시지 생성 함수 실행
        docs = retriever.invoke(message) # 사용자가 입력한 질문을 통해 문서에서 관련된 부분 추출(page_content)
        docs = "\n\n".join(document.page_content for document in docs ) # docs(추출된 문서)리스트 안에서 각 추출된 문서 덩어리를 가져오고 해당 문서 덩어리의 page_content부분을 가져와서 두줄의 공백으로 join

        # 위에서 생성한 프롬프트 템플릿 사용하여 최종 프롬프트 생성
        prompt = template.format_messages(context=docs, question=message)
        st.write(prompt)

        # 여기서 llm 모델 실햏하는 것까지 들어가면 체인없이 수동으로 RAG 과정 실행하는 것

else:
    # 처음 파일 업로드 되지 않았을 시 실행
    # 중간에 파일 삭제되었을 때, 메시지 초기화를 위해 실행
    st.write("파일을 업로드 해주세요.")
    st.session_state["messages"] = []