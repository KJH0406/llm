from langchain.document_loaders import SitemapLoader
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings

import streamlit as st
from fake_useragent import UserAgent
ua = UserAgent()


# soup을 인자로 전달, 즉 HTML 전체가 인자로 전달됨.
def parse_page(soup: BeautifulSoup):
    # 헤어 찾아서 제거
    header = soup.find("header")
    footer = soup.find("footer")
    if header:
        header.decompose() # decompose : 태그와 내용을 분리해줌
    if footer:
        footer.decompose()
    return str(soup.get_text()).replace("\n", " ")



# 사이트 맵 로드(동일 url 캐싱 처리)
# @st.cache_data(show_spinner="사이트맵을 로딩 중입니다.")
def load_website(url):
    # RAG를 위한 스플리터 지정
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000,
    chunk_overlap=200,
    )

    # 사이트 맵 로드
    loader = SitemapLoader(
        url,
        parsing_function=parse_page
        )
    loader.headers = {'User-Agent': ua.random}
    loader.requests_per_second = 2 # 너무 빠르게 크롤링하면 차단당할 수 있기 때문에 시간 설정

    # loader를 통해서 문서를 받아오고 text_splitter로 위에서 정의해놓은 splitter사용하여 문서 텍스트 분할
    docs = loader.load_and_split(text_splitter=splitter)

    # 충분히 분할된 문서를 기반으로 백터 스토어에 임베딩하여 저장
    vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())

    # 검색기 반환
    return vector_store.as_retriever()

# 페이지 인터페이스 설정
st.title("Site Crawler")

# 사이드바 위젯 설정
with st.sidebar:
    # 크롤링할 페이지 주소
    url = st.text_input("페이지 주소를 입력해주세요", placeholder="https://example.com")

if url:
    if ".xml" in url:
        retriever = load_website(url)
        docs = retriever.invoke("GPT-4 터보의 요금은 얼마입니까?")
        
    else:
        with st.sidebar:
            st.error("/sitemap.xml 을 주소를 추가해주세요(* xml파일을 찾지 못했을 수도 있습니다.")


