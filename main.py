from typing import Any, Dict
from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# 서버 구축
app = FastAPI(
    title="Jang Ho Maximus Quote Giver", # 이름
    description="Get a real quote said by Jang Ho Maximus himself.", # 설명
    servers=[
        {"url":"https://blond-nursery-touring-rd.trycloudflare.com"} # 제공될 서버 URL을 설정
    ]
)

# 명언의 데이터 형식 지정
class QuoteArgsSchema(BaseModel):
		# 'quote' 필드를 정의
    quote: str = Field( # 문자열 타입
        description="The quote that Jang Ho Maximus said.",
    )
    # 'year' 필드를 정의 
    year: int = Field( # 정수 타입
        description="The year when Jang Ho Maximus said the quote.",
    )

# 데코레이터를 사용하여 '/quote' 엔드포인트에 대한 GET 요청을 get_quote 함수를 사용하여 처리
@app.get(
    "/quote", # 엔드포인트 URL 설정

    summary="Returns a random quote by Jang Ho Maximus",

    description="Upon receiving a GET request this endpoint will return a real quiote said by Jang Ho Maximus himself.",

    response_description="A Quote object that contains the quote said by Jang Ho Maximus and the date when the quote was said.",
    
    response_model=QuoteArgsSchema, # 응답 모델로 사용할 데이터 스키마(명언: 문자열 타입, 연도: 정수 타입) 설정
    )
# '/quote' 엔드포인트로 GET 요청이 들어왔을 때 실행
def get_quote(request: Request):
    print(request.headers)
    return {
        "quote": "삶은 짧다...먹고 싶은거 다먹어라..",
        "year": 2024,
    }

# 임의의 유저 토큰 생성
user_token_db = {
    "ABCDEF": "jangho"
}

@app.get(
    "/authorize",
    response_class=HTMLResponse,
)
def handle_authorize(client_id: str, redirect_uri: str, state:str):
    return f"""
    <html>
        <head>
            <title>Quote Log In</title>
        </head>
        <body>
            <h1>Log Into Quote</h1>
            <a href="{redirect_uri}?code=ABCDEF&state={state}">Authorize</a>
        </body>
    </html>
    """

@app.post("/token")
def handle_token(code=Form(...)):
    return {
        "access_token": user_token_db[code],
    }

    