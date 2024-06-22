from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.storage import LocalFileStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.retrievers import WikipediaRetriever 
import streamlit as st

st.set_page_config(
    page_title="Output parser",
    page_icon="🔗",
)

st.title("Output parser")

llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0,
    streaming=True,
    callbacks=[
        StreamingStdOutCallbackHandler()
    ],
)

# 파일을 읽고 텍스트 분할
@st.cache_data(show_spinner="파일을 처리하는 중입니다...") # 데이터 캐싱
def split_file(file):
    # 업로드된 파일 처리
    file_content = file.read() 
    file_path = f"./.cache/quiz_files/{file.name}" 
    with open(file_path, "wb") as f: 
        f.write(file_content) 
        # 텍스트 스플리터 설정
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        # separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        )
        loader = UnstructuredFileLoader(file_path)
        docs = loader.load_and_split(text_splitter=splitter)
        return docs


# 퀴즈 생성 방식 설정
with st.sidebar:
    docs = None
    choice = st.selectbox("방식을 선택해주세요.", (
        "내 파일 사용", "위키피디아 사용",
    ))
    if choice == "내 파일 사용":
        file = st.file_uploader("파일을 업로드해주세요.", type=["pdf, txt", "docx", "md"])
        if file:
            docs = split_file(file)
    else:
        topic = st.text_input("주제를 입력해주세요.")
        if topic:
            retriever = WikipediaRetriever(top_k_results=5)
            with st.status("관련 내용을 검색 중입니다..."):
                docs = retriever.get_relevant_documents(topic)

# 문서 리스트 포맷팅
def formatting_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

# 초기 화면 설정(파일 업로드 되지 않았을 때)
if not docs:
    st.markdown(
        """
        ‼️ 퀴즈 생성 방법(택 1)
        1. 파일을 업로드한다. 
        2. 위키피디아에 주제를 검색한다.
        """
    )
else:
    st.write(docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a helpful assistant that is role playing as a teacher.
            
                Based ONLY on the following context make 10 questions to test the user's knowledge about the text.
                
                Each question should have 4 answers, three of them must be incorrect and one should be correct.
                    
                Use (o) to signal the correct answer.

                Questions and answers must be written in Korean.
                    
                Question examples:
                    
                Question: What is the color of the ocean?
                Answers: Red|Yellow|Green|Blue(o)
                    
                Question: What is the capital or Georgia?
                Answers: Baku|Tbilisi(o)|Manila|Beirut
                    
                Question: When was Avatar released?
                Answers: 2007|2001|2009(o)|1998
                    
                Question: Who was Julius Caesar?
                Answers: A Roman Emperor(o)|Painter|Actor|Model
                    
                Your turn!
                    
                Context: {context}
                """
            )
        ]
    ) 


    chain = {"context": formatting_docs}|prompt | llm

    start = st.button("생성하기")

    if start:
        response = chain.invoke(docs).content
        if response:
            st.write(response)