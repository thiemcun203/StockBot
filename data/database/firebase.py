import streamlit as st
from google.cloud import firestore
import json
from google.oauth2 import service_account
import time
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="stockbot-demo")

# Create a reference to the Google post.
DB = db.collection("user_chat")
data = {
            "timestamp": time.time(),
            "user_message": "33re",
            "bot_message": "ddff",
            "context_id": "dddf",
            "like": None,
            "feedback": None,
            "time_feedback": time.time()
        }

# Optionally, retrieve the ID of the newly added document
new_document_ref, new_document_id = DB.add(data)

print(f"New document ID: {new_document_id},{new_document_ref}")

# doc = DB.document(new_document_id)
# new_data = {
#             "timestamp": time.time(),
#             "user_message": "33re",
#             "bot_message": "ddff",
#             "context_id": "dddf",
#             "like": None,
#             "feedback": None,
#             "time_feedback": time.time()
#         }
# doc.update(new_data)
# print("Document updated successfully.")
# Let's see what we got!
# st.write("The id is: ", doc.id)
# st.write("The contents are: ", doc.to_dict())