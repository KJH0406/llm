from langchain.document_loaders import SitemapLoader
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

import streamlit as st
from fake_useragent import UserAgent
ua = UserAgent()


llm = ChatOpenAI(
    temperature=0.1,
)


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
@st.cache_data(show_spinner="사이트맵을 로딩 중입니다.")
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

answers_prompt = ChatPromptTemplate.from_template(
"""
    Using ONLY the following context answer the user's question. If you can't just say you don't know, don't make anything up.
                                                  
    Then, give a score to the answer between 0 and 5.
    If the answer answers the user question the score should be high, else it should be low.
    Make sure to always include the answer's score even if it's 0.
    Context: {context}
                                                  
    Examples:
                                                  
    Question: How far away is the moon?
    Answer: The moon is 384,400 km away.
    Score: 5
                                                  
    Question: How far away is the sun?
    Answer: I don't know
    Score: 0
                                                  
    Your turn!
    Question: {question}
"""
)

def get_answers(inputs):
    contexts = inputs["contexts"]
    question = inputs["question"]

    answers_chain = answers_prompt | llm
    answers = []
    for context in contexts:
        result = answers_chain.invoke({
            "question":question,
            "context":context.page_content,
        })
        answers.append({
            "answer": result.content, # 답변 컨텐츠
            "source": context.metadata["source"].strip(), # 답변 출처
            # "metadata": context.metadata, # 메타 데이터 확인
            # "date": context.metadata["lastmod"], # 수정 날짜
        })   


    return {
        "question": question,
        "answers": answers,
    }

choose_prompt = ChatPromptTemplate.from_messages(
     [
        (
            "system",
            """
            Use ONLY the following pre-existing answers to answer the user's question.
            Use the answers that have the highest score (more helpful).
            Cite sources and return the sources of the answers as they are, do not change them.
            Answers: {answers}
            """,
        ),
        ("human", "{question}"),
    ]
)


def choose_answer(inputs):
    question=inputs["question"]
    answers=inputs["answers"]
    choose_chian = choose_prompt | llm
    answer_texts = ""

    for answer in answers:
        answer_texts += f'Answer:{answer["answer"]}\nSurece:{answer["source"]}\n\n'

    return choose_chian.invoke({
        "question": question,
        "answers": answers
    })



# 페이지 인터페이스 설정
st.title("Site Crawler")

# 사이드바 위젯 설정
with st.sidebar:
    # 크롤링할 페이지 주소
    url = st.text_input("페이지 주소를 입력해주세요", placeholder="https://example.com")

if url:
    if ".xml" in url:
        retriever = load_website(url)
        query = st.text_input("웹사이트에 대한 질문을 입력하세요")
        if query:
            # 사용자가 질문을 하고 관련된 문서를 추출하고 사용자 질문에 대한 응답(context)을 생성하는 체인
            chain = ({
                "contexts": retriever, # 2. retriever를 통해 contexts(질문과 관련된 문서 조각들)가 생성되고
                "question": RunnablePassthrough(),  # 1. 사용자가 질문을 입력하고 그대로 반영
            } 
            | RunnableLambda(get_answers) # 3. 위에서 생성된 contexts가 get_answers함수의 인자로 전달됨
            | RunnableLambda(choose_answer) # 4. get_answers함수를 통해 생성된 답변(results)들이 choose_answer 함수의 인자로 전달
            )
            
            result = chain.invoke(query) # 0. 사용자 질문 전달
            st.write(result.content) #5. choose_answer함수를 통해 생성된 결과 작성
    else:
        with st.sidebar:
            st.error("/sitemap.xml 을 주소를 추가해주세요(* xml파일을 찾지 못했을 수도 있습니다.")


