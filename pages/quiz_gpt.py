from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.retrievers import WikipediaRetriever 
from langchain.schema import BaseOutputParser
import streamlit as st
import json

# 인터페이스 설정
st.set_page_config(
    page_title="Output parser",
    page_icon="🔗",
)
st.title("Output parser")


# JSON 형식으로 변환
class JsonOutputParser(BaseOutputParser):
    def parse(self, text):  
        # 입력된 텍스트를 JSON 형식으로 변환
        text = text.replace("```", "").replace("json", "")
        return json.loads(text)

# 클래스 인스턴스를 생성
output_parser = JsonOutputParser()

# LLM 모델 설정
llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0,
    streaming=True,
    callbacks=[
        StreamingStdOutCallbackHandler()
    ],
)

# 여러 문서를 하나로 병합
def formatting_docs(docs):
    # 문서의 내용을 두 줄 간격으로 합쳐서 반환
    return "\n\n".join(document.page_content for document in docs)

# 문서를 기반으로 Q&A 생성
question_prompt = ChatPromptTemplate.from_messages(
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
question_chain = {"context": formatting_docs} | question_prompt | llm

# Q&A 생성 결과를 JSON 형태로 변환
formatting_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a powerful formatting algorithm.
     
            You format exam questions into JSON format.
            Answers with (o) are the correct ones.

            Questions and answers must be written in Korean.
            
            Example Input:
            Question: What is the color of the ocean?
            Answers: Red|Yellow|Green|Blue(o)
                
            Question: What is the capital or Georgia?
            Answers: Baku|Tbilisi(o)|Manila|Beirut
                
            Question: When was Avatar released?
            Answers: 2007|2001|2009(o)|1998
                
            Question: Who was Julius Caesar?
            Answers: A Roman Emperor(o)|Painter|Actor|Model
            
            
            Example Output:
            
            ```json
            {{ "questions": [
                    {{
                        "question": "What is the color of the ocean?",
                        "answers": [
                                {{
                                    "answer": "Red",
                                    "correct": false
                                }},
                                {{
                                    "answer": "Yellow",
                                    "correct": false
                                }},
                                {{
                                    "answer": "Green",
                                    "correct": false
                                }},
                                {{
                                    "answer": "Blue",
                                    "correct": true
                                }},
                        ]
                    }},
                                {{
                        "question": "What is the capital or Georgia?",
                        "answers": [
                                {{
                                    "answer": "Baku",
                                    "correct": false
                                }},
                                {{
                                    "answer": "Tbilisi",
                                    "correct": true
                                }},
                                {{
                                    "answer": "Manila",
                                    "correct": false
                                }},
                                {{
                                    "answer": "Beirut",
                                    "correct": false
                                }},
                        ]
                    }},
                                {{
                        "question": "When was Avatar released?",
                        "answers": [
                                {{
                                    "answer": "2007",
                                    "correct": false
                                }},
                                {{
                                    "answer": "2001",
                                    "correct": false
                                }},
                                {{
                                    "answer": "2009",
                                    "correct": true
                                }},
                                {{
                                    "answer": "1998",
                                    "correct": false
                                }},
                        ]
                    }},
                    {{
                        "question": "Who was Julius Caesar?",
                        "answers": [
                                {{
                                    "answer": "A Roman Emperor",
                                    "correct": true
                                }},
                                {{
                                    "answer": "Painter",
                                    "correct": false
                                }},
                                {{
                                    "answer": "Actor",
                                    "correct": false
                                }},
                                {{
                                    "answer": "Model",
                                    "correct": false
                                }},
                        ]
                    }}
                ]
            }}
            ```
             Your turn!
             Input: {context}
            """
            
        )
    ]
)
formatting_chain = formatting_prompt | llm

# Q&A 생성 및 포맷팅 실행 함수
@st.cache_data(show_spinner="Q&A를 작성 중입니다...")
def run_QnA_chain(_docs, topic):
    chain = {"context": question_chain} | formatting_chain | output_parser
    response = chain.invoke(_docs)
    return response

# 위키피디아 기반 문서 생성
@st.cache_data(show_spinner="파일을 처리하는 중입니다...")
def wiki_search(term):
    retriever = WikipediaRetriever(top_k_results=5)
    docs = retriever.get_relevant_documents(term)
    return docs

# 사용자가 업로드한 문서 기반 생성
@st.cache_data(show_spinner="파일을 처리하는 중입니다...") 
def split_file(file):
    file_content = file.read() 
    file_path = f"./.cache/quiz_files/{file.name}" 
    with open(file_path, "wb") as f: 
        f.write(file_content) 
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
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
            docs = wiki_search(topic)
            

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
    # 퀴즈 생성 방법이 설정되어 docs가 생성되면 해당 docs를 기반으로 Q&A 생성
    response = run_QnA_chain(docs, topic if topic else file.name)

    # 결과물 UI 생성(streamlit form 활용)
    with st.form("questions_form"):
        for question in response["questions"]:
            st.write(question["question"])
            st.radio("답변을 선택하세요.", [answer["answer"] for answer in question["answers"]],
            index=None # 초기에 아무것도 선택하지 않음.
            )
        st.form_submit_button("Submit")