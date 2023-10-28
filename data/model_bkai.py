from sentence_transformers import SentenceTransformer

# INPUT TEXT MUST BE ALREADY WORD-SEGMENTED!
# sentences = ["Cô ấy là một người vui_tính .", "Cô ấy cười nói suốt cả ngày ."]

model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')

# import numpy as np
# import json
# from sklearn.metrics.pairwise import cosine_similarity
# from mm import model
# # embeddings = model.encode(sentences)
# embedding_model = model

# # Load the JSON data from the provided file
# with open("/Users/nguyenbathiem/Documents/GitHub/StockBot/StockBot/data/splitted_news.json", "r") as file:
#     data = json.load(file)

# # Extract the 'Splitted Content' from the data
# contents = [item['Splitted Content'] for item in data]

# Initialize the SentenceTransformer model
# embedding_model = SentenceTransformer('bkai-foundation-models/vietnamese-bi-encoder')

# Compute embeddings for each content
# embeddings = embedding_model.encode(contents)

# # Compute the pairwise cosine similarities
# cosine_similarities = cosine_similarity(embeddings)

# # Since cosine_similarity returns a symmetric matrix and the diagonal is 1 (since a content is always 100% similar to itself), 
# # we will mask the upper triangular part including the diagonal to avoid duplicate pairs and self-pairs.
# mask = np.triu(np.ones_like(cosine_similarities, dtype=bool))
# cosine_similarities[mask] = 0

# # Find the pair of contents with the highest similarity
# content_pair_indices = np.unravel_index(np.argmax(cosine_similarities, axis=None), cosine_similarities.shape)
# similarity_value = cosine_similarities[content_pair_indices]

# print(content_pair_indices, similarity_value)
