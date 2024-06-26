from langchain.schema import SystemMessage
import streamlit as st
import os
import requests
from typing import Type
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain.agents import initialize_agent, AgentType
from langchain.utilities import DuckDuckGoSearchAPIWrapper

llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o")

alpha_vantage_api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")

# 주식 심볼 검색 도구(특정 주식의 공개 단위를 식별)
class StockMarketSymbolSearchToolArgsSchema(BaseModel):
    query: str = Field(
        description="The query you will search for.Example query: Stock Market Symbol for Apple Company"
    )
class StockMarketSymbolSearchTool(BaseTool):
    name = "StockMarketSymbolSearchTool"
    description = """
    Use this tool to find the stock market symbol for a company.
    It takes a query as an argument.
    
    """
    args_schema: Type[
        StockMarketSymbolSearchToolArgsSchema
    ] = StockMarketSymbolSearchToolArgsSchema

    def _run(self, query):
        ddg = DuckDuckGoSearchAPIWrapper()
        return ddg.run(query)



# 회사의 재무 개요 분석 도구
class CompanyOverviewArgsSchema(BaseModel):
    symbol: str = Field(
        description="Stock symbol of the company.Example: AAPL,TSLA",
    )
class CompanyOverviewTool(BaseTool):
    name = "CompanyOverview"
    description = """
    Use this to get an overview of the financials of the company.
    You should enter a stock symbol.
    """
    args_schema: Type[CompanyOverviewArgsSchema] = CompanyOverviewArgsSchema

    def _run(self, symbol):
        r = requests.get(
            f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={alpha_vantage_api_key}"
        )
        return r.json()


# 회사 소득 보고서 도구
class CompanyIncomeStatementTool(BaseTool):
    name = "CompanyIncomeStatement"
    description = """
    Use this to get the income statement of a company.
    You should enter a stock symbol.
    """
    args_schema: Type[CompanyOverviewArgsSchema] = CompanyOverviewArgsSchema

    def _run(self, symbol):
        r = requests.get(
            f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={alpha_vantage_api_key}"
        )
        return r.json()["annualReports"]

# 회사 주식 성과 도구
class CompanyStockPerformanceTool(BaseTool):
    name = "CompanyStockPerformance"
    description = """
    Use this to get the weekly performance of a company stock.
    You should enter a stock symbol.
    """
    args_schema: Type[CompanyOverviewArgsSchema] = CompanyOverviewArgsSchema

    def _run(self, symbol):
        r = requests.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={alpha_vantage_api_key}"
        )
        response = r.json()
        return list(response["Weekly Time Series"].items())[:200]


agent = initialize_agent(
    llm=llm,
    verbose=True,
    agent=AgentType.OPENAI_FUNCTIONS,
    handle_parsing_errors=True,
    tools=[
        StockMarketSymbolSearchTool(), # 주식 심볼 검색 도구(특정 주식의 공개 단위를 식별)
        CompanyOverviewTool(), # 회사의 재무 개요 분석 도구
        CompanyIncomeStatementTool(), # 회사의 소득 보고서 도구
        CompanyStockPerformanceTool(), # 회사의 주식 성과 도구

        # 회사 정보 검색: 주식 시장 심볼을 검색하고, 회사의 기본 정보를 제공.
        # 재무 개요 제공: 회사의 재무 상태와 관련된 개요 정보를 제공.
        # 소득 보고서 분석: 회사의 연간 소득 보고서를 제공하여 재무 성과를 분석.
        # 주식 성과 평가: 회사 주식의 주간 성과를 분석하여 최근 성과를 평가.
    ],
    agent_kwargs={
        "system_message": SystemMessage(
            content="""
            You are a hedge fund manager.

            You evaluate a company and provide your opinion and reasons why the stock is a buy or not.
            
            Consider of a variety of information available for analysis.
            
            Be assertive in your judgement and recommend the stock or advise the user against it.

            Responses must be translated and written in Korean.
            """
            # 당신은 헤지펀드 매니저입니다.

            # 회사를 평가하고 그 주식이 매수할 만한지에 대한 의견과 이유를 제공합니다.

            # 분석에 사용할 수 있는 다양한 정보를 고려합니다.

            # 당신의 판단에 대해 단호하게 말하고, 주식을 추천하거나 사용자가 주식을 매수하지 않도록 조언하십시오.
        )
    },
)

st.set_page_config(
    page_title="투자 도우미",
    page_icon="💼",
)

st.markdown(
    """
    # 투자 도우미

    회사 이름을 입력하시면, 에이전트가 해당 회사에 대한 조사를 해드립니다.
"""
)

company = st.text_input("관심 있는 회사 이름을 입력하세요. (* 나스닥)")

if company:
    result = agent.invoke(company)
    st.write(result["output"].replace("$", "\$"))