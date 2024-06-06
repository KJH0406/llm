- templates, output parser, chat 등을 | 연산자로 chain을 형성한 다음에
  - chain 1, chain2 이런식으로 엮어서 여러가지의 체인을 형성하고, 이를 통해서 더 좋은 결과물을 얻을 수 있을 것 같음.
    - **like 문서 전처리[chain_1] → 전처리된 문서로 매뉴얼 작성[chain_2] → 작성된 매뉴얼로 챗봇에 사용[chain_3]**
- **FewShotPromptTemplate**
  [Few-shot prompt templates | 🦜️🔗 LangChain](https://python.langchain.com/v0.1/docs/modules/model_io/prompts/few_shot_examples/)
  - prompt template 사용하는 이유?
    - prompt template을 디스크에 저장하고 load해서 사용할 수 있기 때문.
    - 나중에 규모가 큰 언어 모델 설계할때 db나 파일 등에서 prompt 로드해서 사용
  - **FewShotPromptTemplate 의 유용성**
    - 구체적인 답안이 필요할때는 프롬프트를 사용해서 어떻게 대답해야하는지를 알려주는 것 보다 모델에게 어떻게 대답해야하는지에 대한 예제를 주는 것이 더 효과적임!
      - 예를 들어, 뭐 문장 사이마다 콤마 넣어줘 이런식으로 프롬프팅 하는 것보다 그냥 콤마가 담긴 문장의 예시를 주는 것이 좋음.
    - **고객 지원에 활용할 수 있는 방법**
      - **대화 기록같은 것들을 DB에서 가져와서 FewShotPromptTemplate 을 사용하여 형식화시켜주면 더 빠르게 만들 수 있음!**
  - **LengthBasedExampleSelector**
    - 너무 많은 예시를 프롬프트에 담으면 비용이 많이 들음.
    ```
    prompt = FewShotPromptTemplate(
        example_prompt=example_prompt,
        examples=examples, #  모델 학습에 사용될 예제의 목록
        **위와 같이 구성하면 예시 목록에 있는 모든 예제가 다 포함이 되어버림. 이래서 비용 많이 들음
        그래서 exampleSelector사용해서 해당 예제 중에 내가 설정한 조건에 맞는 예제만 선택됨.**


        suffix="Human: What do you know about {country}?", # 템플릿의 끝부분에 추가될 문자열
        input_variables=["country"], # 템플릿에서 사용될 입력 변수
    )
    ```
  - **Serialization and Composition**
    - 디스크에서 프롬프트 템플릿 가져오는 방법
      - json이나 yml파일 통해서 외부에 저장한 후, prompt load해서 사용할 수 있음.[이미 하고 있었음]
      - 여러가지의 프롬프트를 병합하는 방법도 있는데 현재로서 필요성을 못느껴서 일단 코드만 저장
  - **Cashing**
    ```
    from langchain.globals import set_llm_cache # 언어 모델 응답 저장(캐싱)
    # => 똑같은 질문을 받으면 다시 생성하지 않고 기존에 응답했던 내용으로 응답
    from langchain.cache import InMemoryCache

    set_llm_cache(InMemoryCache()) # 이렇게 구성하면 모든 response가 메모리에 저장됨.
    ```
    - 캐싱을 통해서 언어 모델의 응답 또한 저장 할 수 있음!
      - 현재는 벡터 DB에만 사용해봤음. 그렇지만 앞으로는 모델에게하는 질문이나 응답에도 사용해볼것!
    - **디비에 캐싱걸어서 응답 생성할수도 있음!!!!!**
      - 메모리에 캐싱하면 리부팅 시 다 날라감 그래서 질문이나 응답을 디비에 캐싱해서 할 수 있음!
      ```
      from langchain.globals import set_llm_cache
      from langchain.cache import SQLiteCache # sqlite 사용

      set_llm_cache(SQLiteCache("cash.db")) # 이렇게 구성하면 메모리가 아닌 *DB* 에 저장됨!!!
      # 인자(현재 cash.db)에 아무것도 넣지 않으면 기본값은 .langchain.db로 생성
      ```
      - 위 코드 실행 시키면 좌측에 cash.db라는 파일 생성됨!
      - 기존에는 벡터DB만 캐싱했는데, 이제는 질문과 응답결과까지 캐싱하여 비용을 확연하게 낮출 수 있음!
  - **Debug**

    - from langchain.globals import set_debug
      ```python
      from langchain.globals import set_debug # 디버거 기능을 통해서 로그를 확인 할 수 있음!
      # 향후 체인 작업할 때 각 과정을 디버깅할 수 있어서 매우 유용!

      set_debug(True)
      ```

  - **Serialization**
    - OpenAI api 호출할때 드는 비용 디버깅
      - 이건 나중에 본 코드에서 한번 써보고 비용 체크해보기
    - 커스텀한 모델을 저장하고 불러오는 방법
      - 이건 크게 필요없을 것 같아서 패스
