import os
from langchain_community.document_loaders import TextLoader
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_mistralai.embeddings import MistralAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]

txt_file_path = "populate_db_vector/data/recipes_output.txt"
faiss_index_path = "llm_response/data/faiss_index"

loader = TextLoader(txt_file_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)

embeddings = MistralAIEmbeddings(model="mistral-embed", mistral_api_key=api_key)

if os.path.exists(faiss_index_path):
    print("Loading FAISS index from disk...")
    vector = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
else:
    print("Creating FAISS index...")
    vector = FAISS.from_documents(documents, embeddings)
    
    vector.save_local(faiss_index_path)

retriever = vector.as_retriever()

model = ChatMistralAI(mistral_api_key=api_key)

prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}""")

document_chain = create_stuff_documents_chain(model, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

response = retrieval_chain.invoke({"input": "I'm gluten intolerant. Give me some recipes."})
print(response["answer"])
