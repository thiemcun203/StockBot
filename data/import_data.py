import itertools
import json
from sentence_transformers import SentenceTransformer
import pinecone
with open('/Users/nguyenbathiem/Coding/Semester V/StockBot/splitted_news.json', 'r') as file:
    data = json.load(file)
    
embedding_model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder') #768 dims

pinecone.init(api_key="7e35d994-0165-4d6f-b71d-5ccac86b3bdd", environment="gcp-starter")
index = pinecone.Index("bkai-model-stockbot")

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

# try:
# for i, seg in enumerate(data[:10]):
#     document = data[i]["Splitted Content"]
#     embedded_word = embedding_model.encode(document).tolist()
#     metadata = {"Splitted Content" :data[i]["Splitted Content"],
    #             "URL": data[i]["URL"], 
#                 "Splitted Title": data[i]["Splitted Title"], 
#                 "Publish Time": data[i]["Publish Time"], 
#                 "ID Nganh Cap 3": data[i]["ID Nganh Cap 3"],
#                 "Nganh Cap 3": data[i]["Nganh Cap 3"],
#                 "ID Nganh Cap 4": data[i]["ID Nganh Cap 4"],
#                 "Nganh Cap 4": data[i]["Nganh Cap 4"],
#                 "News ID": data[i]["News ID"],
#                 "ID": data[i]["ID"],
#                 }
        # if i % 100 == 0:
        #     time.sleep(1)
        #     print(i, "done")
#     # print((document,embedded_word, metadata))
#     index.upsert([(document,embedded_word, metadata)])
# except:
#     print("error" + str(i))


# for chunk in chunks(example_data_generator(), batch_size=100):
#     index.upsert(vector = chunk)

# demo
# embedded_word = embedding_model.encode(data[0]["Splitted Content"]).tolist()
# metadata = {"Splitted Content" :data[0]["Splitted Content"],
#             "URL": data[0]["URL"], 
#             "Splitted Title": data[0]["Splitted Title"], 
#             "Publish Time": data[0]["Publish Time"], 
#             "ID Nganh Cap 3": data[0]["ID Nganh Cap 3"],
#             "Nganh Cap 3": data[0]["Nganh Cap 3"],
#             "ID Nganh Cap 4": data[0]["ID Nganh Cap 4"],
#             "Nganh Cap 4": data[0]["Nganh Cap 4"],
#             "News ID": data[0]["News ID"],
#             "ID": data[0]["ID"],
#             }
# index.upsert([('id-1',embedded_word, metadata)])


