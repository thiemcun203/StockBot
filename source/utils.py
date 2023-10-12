from sentence_transformers import SentenceTransformer
import openai
import streamlit as st
from apikey import apikey
import chromadb

#add apikey of gpt model
openai.api_key = apikey

#import vector database
client = chromadb.Client()
client = chromadb.PersistentClient(path="vectorizeData")
news_vectorize_data = client.get_or_create_collection(name='news_vectorize_data')

#vietnamese embedding model
embedding_model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')

def find_match(input:str, top_k = 3):
    '''Function returns the top k most relevant news articles from the database given the input query'''
    input_em = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder').encode(input).tolist()
    results = news_vectorize_data.query(query_embeddings = input_em, 
                                       n_results = top_k)
    return (results, results['documents'][0][0] + "\n" + results['documents'][0][1] + "\n" + results['documents'][0][2])

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
    results = news_vectorize_data.query(
    query_embeddings=[SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder').encode("lãi suất agribank?").tolist()],
    n_results= 3
    )
    print(f'''Tìm hiểu thêm tại:
1. {results['metadatas'][0][0]['URL']} 
2. {results['metadatas'][0][1]['URL']}
3. {results['metadatas'][0][2]['URL']}''')
    # print(results)