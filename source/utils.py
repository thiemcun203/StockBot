from sentence_transformers import SentenceTransformer
import openai
import streamlit as st
from apikey import apikey
import pinecone

#add apikey of gpt model
openai.api_key = st.secrets["gpt_apikey"]

#import vector database
pinecone.init(api_key=st.secrets["pinecone_apikey"], environment="gcp-starter")
index = pinecone.Index("bkai-model-stockbot")

#vietnamese embedding model
embedding_model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')

def find_match(input:str, top_k = 3):
    '''Function returns the top k most relevant news articles from the database given the input query'''
    input_em = embedding_model.encode(input).tolist()
    results = index.query(vector = input_em, 
                                       top_k = top_k,
                                       include_metadata=True)
    return (results, results['matches'][0]['metadata']['Splitted Content'] + "\n" + results['matches'][1]['metadata']['Splitted Content'] + "\n" + results['matches'][2]['metadata']['Splitted Content'])

def query_refiner(conversation, query):
    prompt=str(f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:")
    completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = [{'role': 'user', 'content': prompt}],
    max_tokens=1200,
    temperature = 0)
    response=completion['choices'][0]['message']['content']
    return response
    
def get_conversation_string():
    '''Concatenates the conversation log into a string'''
    conversation_string = ""
    for i in range(len(st.session_state['responses'])-1):
        
        conversation_string += "Human: "+st.session_state['requests'][i] + "\n"
        conversation_string += "Bot: "+ st.session_state['responses'][i+1] + "\n"
    return conversation_string

if __name__ == "__main__":
    
    results = index.query(
    vector=embedding_model.encode("lãi suất agribank?").tolist(),
    top_k= 3,
    include_metadata=True,
    )
    print(f'''Tìm hiểu thêm tại:
1. {results['matches'][0]['metadata']['URL']} 
2. {results['matches'][1]['metadata']['URL']}
3. {results['matches'][2]['metadata']['URL']}''')
    # print(results)