import itertools
import json
from sentence_transformers import SentenceTransformer
import pinecone
with open('/Users/nguyenbathiem/Coding/Semester V/StockBot/splitted_news.json', 'r') as file:
    data = json.load(file)
    
embedding_model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder') #768 dims

pinecone.init(api_key="", environment="gcp-starter")
index = pinecone.Index("bkai-model-stockbot")
# input_em = embedding_model.encode("tinh hinh agribank?").tolist()
# results = index.query(vector = input_em, top_k = 3,include_metadata=True)
# print(results)

example_data_generator = map(
    lambda i: (f'id-{i}', embedding_model.encode(data[i]["Splitted Content"]).tolist(), 
               {"Splitted Content" :data[i]["Splitted Content"],
                "URL": data[i]["URL"], 
                "Splitted Title": data[i]["Splitted Title"], 
                "Publish Time": data[i]["Publish Time"], 
                "ID Nganh Cap 3": data[i]["ID Nganh Cap 3"],
                "Nganh Cap 3": data[i]["Nganh Cap 3"],
                "ID Nganh Cap 4": data[i]["ID Nganh Cap 4"],
                "Nganh Cap 4": data[i]["Nganh Cap 4"],
                "News ID": data[i]["News ID"],
                "ID": data[i]["ID"],
                }),
    range(len(data))
)
def chunks(iterable, batch_size=10):
    """Yield successive n-sized chunks from iterable."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))

with pinecone.Index('bkai-model-stockbot', pool_threads = 30) as index:
    async_results = [
        index.upsert(vectors = ids_vectors_chunk,async_req = True)
        for ids_vectors_chunk in chunks(example_data_generator, batch_size=100)
    ]



