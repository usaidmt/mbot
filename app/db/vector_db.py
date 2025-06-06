import chromadb
from chromadb.config import Settings
import textwrap
import uuid
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Query

load_dotenv()
db_directory = os.getenv("DB_DIRECTORY")

# chroma_settings = Settings(persist_directory=os.getenv("DB_DIRECTORY"))
# chroma_client = Client(chroma_settings)
client = chromadb.PersistentClient(path=os.getenv("DB_DIRECTORY"))


def create_collection(collection_name: str = Query(...)):
    try:
        collection = client.create_collection(name=collection_name)
        return {"message": f"Collection '{collection_name}' created successfully."}
    except Exception as e:
        raise e


def get_collection(directory, collection_name):
    try:
        client = chromadb.PersistentClient(path=directory)

        # List all collections and check if the collection_name exists
        collection_name_lower = ( collection_name.lower().strip() )  # Lowercase and trim the collection name
        existing_collection_names = [ name.lower().strip() for name in client.list_collections() ]

        # if collection_name in client.list_collections():
        if collection_name_lower in existing_collection_names:
            return client.get_collection(collection_name)
        else:
            raise Exception(500, "Collection not found!")

    except Exception as e:
        raise Exception(str(e))


# Function to add data to Chroma DB with embedding
def add_to_chroma(collection_name, content):
    try:
        chunk_size = 10000
        chunks = textwrap.wrap(content, chunk_size)
        collection = get_collection(db_directory, collection_name)

        document_ids = []  # Initialize an empty list to collect document IDs

        metadatas = [{"role": "user"}]
        for chunk in chunks:
            document_id = str(uuid.uuid4())  # Create a unique document ID
            collection.add(documents=chunk, ids=document_id, metadatas=metadatas)
            document_ids.append(document_id)
        return {"document_ids": document_ids}
    except Exception as e:
        print(e)
        print(f"Error uploading data to chrome: {str(e)}")
        return None


def query_chroma(collection_name, query, k=10):

    try:
        """
        Searches for the most relevant documents in Chroma.
        :param collection: Chroma collection instance.
        :param query: Query text.
        :param k: Number of top results to retrieve.
        :return: List of retrieved documents.
        """

        collection = get_collection(db_directory, collection_name);
        results = collection.query(query_texts=[query], n_results=k);
        # return results["documents"];
        return results["documents"][0];
    except Exception as e:
        raise e;

def query_chroma_by_id(collection_name, id_array):

    collection = get_collection(db_directory, collection_name)
    results = collection.get(ids=id_array)


def query_chroma_n_club_document_title(collection_name, query, k=10):
    """
    Searches for the most relevant documents in Chroma.
    :param collection: Chroma collection instance.
    :param query: Query text.
    :param k: Number of top results to retrieve.
    :return: List of retrieved documents.
    """
    collection = get_collection(db_directory, collection_name)
    results = collection.query(query_texts=[query], n_results=k)
    # return results["documents"][0]
    documents_with_ids = []
    for doc, id in zip(results["documents"], results["ids"]):
        # Assuming each metadata contains an 'id' field
        document_data = {
            "id": id,  # Safely extract the id (None if not found)
            "document": doc,  # Document text/content
        }
        documents_with_ids.append(document_data)
    combined_result = [
        {"id": doc_id, "document": doc}
        for doc_id, doc in zip(
            documents_with_ids[0]["id"], documents_with_ids[0]["document"]
        )
    ]
    print(combined_result)
    return combined_result
