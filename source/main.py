from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from utils import *
# from apikey import apikey
import random, time
#   python -m streamlit run source/main.py

# Setup memorize the conversation
if 'buffer_memory' not in st.session_state:
            st.session_state.buffer_memory=ConversationBufferWindowMemory(k=1,return_messages=True)

system_msg_template = SystemMessagePromptTemplate.from_template(template="""Answer the question in Vietnamese as truthfully as possible using the provided context, 
and if the answer is not contained within the text below, say 'Tôi không biết'""")
human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=st.secrets["gpt_apikey"])
conversation = ConversationChain(memory=st.session_state.buffer_memory,prompt=prompt_template, llm=llm, verbose=True)


# setup UI
st.subheader("📈StockBot🤖")
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Tôi có thể giúp gì cho bạn?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="😎" if message["role"] == "user" else "🤖"):
        st.write(message["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="😎"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
           
            results, context = find_match(prompt)
            URL = f'''Tìm hiểu thêm tại: 
1. {results['matches'][0]['metadata']['URL']} 
2. {results['matches'][1]['metadata']['URL']}
3. {results['matches'][2]['metadata']['URL']}'''

            # # get response from model GPT
            # time.sleep(0.5)
            # response = 'Demo Response ' + str(random.randint(0,100)) + '\n\n' + URL
            response = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{prompt}") + '\n\n' + URL
            
            st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)

        



          