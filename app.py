import os
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# 페이지 설정
st.set_page_config(page_title="Azure AI 채팅 어시스턴트", layout="wide")
st.title("🤖 Azure AI 채팅 어시스턴트")

# 환경변수 로드
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_AI_SEARCH_ENDPOINT = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
AZURE_AI_SEARCH_API_KEY = os.getenv("AZURE_AI_SEARCH_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
DEPLOYMENT_EMBEDDING_NAME = os.getenv("DEPLOYMENT_EMBEDDING_NAME")
INDEX_NAME = os.getenv("INDEX_NAME")

# 클라이언트 초기화
chat_client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2024-12-01-preview",
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", 
         "content": "You are a helpful assistant that helps people find information."}
    ]

# 채팅 히스토리 표시
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력
if user_input := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Azure AI Search 파라미터
    rag_params = {
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": AZURE_AI_SEARCH_ENDPOINT,
                    "index_name": INDEX_NAME,
                    "authentication": {
                        "type": "api_key",
                        "key": AZURE_AI_SEARCH_API_KEY,
                    },
                    "query_type": "vector",
                    "embedding_dependency": {
                        "type": "deployment_name",
                        "deployment_name": DEPLOYMENT_EMBEDDING_NAME,
                    },
                }
            }
        ],
    }
    
    # API 호출
    try:
        with st.spinner("응답 생성 중..."):
            response = chat_client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=st.session_state.messages,
                extra_body=rag_params
            )
        
        assistant_message = response.choices[0].message.content
        
        # 어시스턴트 메시지 추가
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        
        # 어시스턴트 응답 표시
        with st.chat_message("assistant"):
            st.markdown(assistant_message)
    
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")