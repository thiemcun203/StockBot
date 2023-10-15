import re
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
import random, time
import pinecone
from streamlit_feedback import streamlit_feedback
#  python -m streamlit run source/main.py

#initialize vector database of news articles
@st.cache_resource 
def connect_vector_database():
    pinecone.init(api_key=st.secrets["apikeys"]["pinecone_apikey"], environment="gcp-starter")
    index = pinecone.Index("bkai-model-stockbot")
    return index
index = connect_vector_database()

# #initialize database for collect user data
@st.cache_resource 
def connect_user():
    from pymongo.mongo_client import MongoClient
    uri = f'mongodb+srv://{st.secrets["db_username"]}:{st.secrets["db_password"]}@cluster0.wgrmih5.mongodb.net/?retryWrites=true&w=majority'
    # Create a new client and connect to the server
    client = MongoClient(uri)

    # # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    user_db = client.get_database('user_chat')
    records = user_db.collect_user_data
    return records
records = connect_user()
    
# Setup memorize the conversation
# st.session_state['buffer_memory'] ="nnn"
if 'buffer_memory' not in st.session_state:
    st.session_state['buffer_memory'] = ConversationBufferWindowMemory(k=1,return_messages=True)

system_msg_template = SystemMessagePromptTemplate.from_template(template="""Answer the question in Vietnamese as truthfully as possible using the provided context,
and if the answer is not contained within the text below, say 'Tôi không biết'""")
human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=st.secrets["apikeys"]["gpt_apikey"])
conversation = ConversationChain(memory=st.session_state.buffer_memory,prompt=prompt_template, llm=llm, verbose=True)

if 'count' not in st.session_state:
    st.session_state.count = 0
st.session_state.count += 1

if 'fb' not in st.session_state:
    st.session_state.fb = 0

if 'data' not in st.session_state:
    st.session_state.data = {}

# setup UI
st.subheader("📈StockBot🤖")
first_message = "Tôi có thể giúp gì cho bạn?"

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": first_message, "feedback":None }]

# Display chat messages
for i,message in enumerate(st.session_state.messages): #do not print all messages
    with st.chat_message(message["role"], avatar="😎" if message["role"] == "user" else "🤖"):
        st.write(message["content"])
    
print("no_of_mess",len(st.session_state.messages))
if prompt := st.chat_input():
    print("entered")  
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="😎"):
        st.write(prompt)
    
# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
           
            results, context = find_match(prompt, index)

            # # get response from model GPT
            # time.sleep(0.5)
            # output = 'Demo Response ' + str(random.randint(0,100)) 
            # response = output
            output = conversation.predict(input=f"Context:\n {context} \n\n Query:\n{prompt}")
            if re.search(r'\bTôi không biết\b', output):
                response = output
            else:
                URL_lst = set([results['matches'][0]['metadata']['URL'], results['matches'][1]['metadata']['URL'], results['matches'][2]['metadata']['URL']])
                URL = "Tìm hiểu thêm tại: \n"
                for i,url in enumerate(URL_lst):
                    URL += f"{i+1}. {url}\n"
                response = output + '\n\n' + URL
            st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
    # save user data
    data = {
            "timestamp": time.time(), #dt_object = datetime.fromtimestamp(timestamp)
            "user_message": st.session_state.messages[-2]["content"],
            "bot_message": st.session_state.messages[-1]["content"],
            "context_id":[results['matches'][0]['id'], results['matches'][1]['id'], results['matches'][2]['id']],
            "like": None,
            "feedback": None
        }
    
    records.insert_one(data)
    st.session_state.data = data
    
    
if st.session_state.count > 1:
    feedback = streamlit_feedback( #each feedback can only used once
                    feedback_type=f"thumbs",
                    key=f"{st.session_state.fb}",
                    optional_text_label="[Tuỳ chọn] Lý do") #after click, reload and add value for next load
    print("feedback",feedback)
    if feedback:
        st.session_state.messages[-1]["feedback"] = feedback
        st.session_state.fb += 1
        data = st.session_state.data
        records.update_one({"timestamp":data["timestamp"]}, {"$set":{
            "feedback_timestamp":time.time(),
            "like": 1 if feedback["score"] == "👍" else 0,
            "feedback": feedback["text"]
            }}, True)
        
         
print(st.session_state.messages[-1])
print("done turn, state",st.session_state.count) 
#each action, fb - refresh page is a turn




          