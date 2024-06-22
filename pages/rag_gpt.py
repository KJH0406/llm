from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
import streamlit as st

# 페이지 인터페이스 설정
st.title("RAG")

# 파일 업로드
file = st.file_uploader("파일을 업로드 해주세요.", type=["pdf", "txt", "docx", "md"]) # 업로드 가능한 파일 확장자 지정


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

# 파일 처리 로직
if file:
    retriever = embed_file(file)
    res = retriever.invoke("3D 프린팅")
    res
