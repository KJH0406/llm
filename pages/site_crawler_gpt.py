from langchain.document_loaders import SitemapLoader

import streamlit as st

# 사이트 맵 로드(동일 url 캐싱 처리)
# @st.cache_data(show_spinner="사이트맵을 로딩 중입니다.")
def load_website(url):
    loader = SitemapLoader(url)
    loader.requests_per_second = 3 # 너무 빠르게 크롤링하면 차단당할 수 있기 때문에 시간 설정
    docs = loader.load()
    return docs

# 페이지 인터페이스 설정
st.title("Site Crawler")

# 사이드바 위젯 설정
with st.sidebar:
    # 크롤링할 페이지 주소
    url = st.text_input("페이지 주소를 입력해주세요", placeholder="https://example.com")

if url:
    if ".xml" in url:
        docs = load_website(url)
        st.write(docs)
    else:
        with st.sidebar:
            st.error("/sitemap.xml 을 주소를 추가해주세요(* xml파일을 찾지 못했을 수도 있습니다.")


