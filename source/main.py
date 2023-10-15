import copy
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import random, time, re, json
import streamlit as st
from utils import *
from streamlit_feedback import streamlit_feedback

#  python -m streamlit run source/main.py

#initialize vector database of news articles
@st.cache_resource 
def connect_vector_database():
    import pinecone
    pinecone.init(api_key=st.secrets["apikeys"]["pinecone_apikey"], environment="gcp-starter")
    index = pinecone.Index("bkai-model-stockbot")
    return index
index = connect_vector_database()

# #initialize database for collect user data
@st.cache_resource 
def connect_user():
    from google.cloud import firestore
    from google.oauth2 import service_account
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    home = firestore.Client(credentials=creds, project="stockbot-demo")
    db = home.collection("user_chat")
    return db
records = connect_user()
    
# Setup memorize the conversation
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
    st.session_state.data = (None,None)
    
if 'double' not in st.session_state: #fix double bug
    st.session_state.double = 0

# setup UI
st.subheader("📈StockBot🤖")
first_message = "Tôi có thể giúp gì cho bạn?"

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": first_message}]

# Display chat messages
for i,message in enumerate(st.session_state.messages): #do not print all messages
    with st.chat_message(message["role"], avatar="😎" if message["role"] == "user" else "🤖"):
        st.write(message["content"])

if prompt := st.chat_input():
    if st.session_state.double + 1 != st.session_state.count:
        st.session_state.double = copy.deepcopy(st.session_state.count)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="😎"):
            st.write(prompt)
        
# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            results, context = find_match(prompt, index)
            # get response from model GPT
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
            "feedback": None,
            "feedback_time": None
        }
    
    _ , ref = records.add(data)
    st.session_state.data = (ref.id,data)

if st.session_state.count > 1:
    feedback = streamlit_feedback( #each feedback can only used once
                    feedback_type=f"thumbs",
                    key=f"{st.session_state.fb}",
                    optional_text_label="[Tuỳ chọn] Lý do") #after click, reload and add value for next load
    if feedback:
        st.session_state.messages[-1]["feedback"] = feedback
        st.session_state.fb += 1 #update feedback id
        
        #retrieve desired data from database
        id, data = st.session_state.data
        doc_ref = records.document(id)
        doc_ref.update({"timestamp":data["timestamp"],
                        "user_message": data["user_message"],
                        "bot_message": data["bot_message"],
                        "context_id": data["context_id"],
                        "like": 1 if feedback["score"] == "👍" else 0,
                        "feedback": feedback["text"],
                        "feedback_time": time.time()
                        })
         
print("Done turn! State: ",st.session_state.count) 
#each action, fb - refresh page is a turn




          