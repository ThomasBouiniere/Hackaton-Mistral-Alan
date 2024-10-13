# my_app/views.py
from django.shortcuts import render
from django.http import HttpResponse
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
from langchain_core.documents import Document
import re

def process_question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        llm_response = apply_your_function(question)  # Remplace par ta fonction
        return render(request, 'llm_response/result.html', {'llm_response': llm_response})
    return render(request, 'llm_response/question_form.html')

def apply_your_function(question):
    load_dotenv()
    api_key = os.environ["MISTRAL_API_KEY"]

    txt_file_path = "populate_db_vector/data/recipes_output.txt"
    faiss_index_path = "llm_response/data/faiss_index"

    loader = TextLoader(txt_file_path)
    docs = loader.load()

    split_documents = []
    for doc in docs:
        split_docs = doc.page_content.split("/")  # Split par le symbole "/"
        for split_doc in split_docs:
            # Créez un nouveau document pour chaque morceau split
            split_documents.append(Document(page_content=split_doc, metadata=doc.metadata))

    # Maintenant, appliquez le text splitter sur les documents splités
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(split_documents)

    embeddings = MistralAIEmbeddings(model="mistral-embed", mistral_api_key=api_key)

    if os.path.exists(faiss_index_path):
        vector = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
    else:
        vector = FAISS.from_documents(documents, embeddings)
        
        vector.save_local(faiss_index_path)

    retriever = vector.as_retriever()

    model = ChatMistralAI(mistral_api_key=api_key)

    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context.
            When asked for a nutritional plan, you must give four recipes per day and answer for as
            many days as asked, with recipes one and three being for snack,
            and recipes two and four being for meal. You must match with the needs of the user. If it is an athlete you must
            choose high-calories recipes with high quantity of proteins. If it is a person who want to loose weight,
            you must choose low-calories recipes with low quantity of carbohydrates and saturated_fatty_acids.

    <context>
    {context}
    </context>
    
    Question: {input}""")

    document_chain = create_stuff_documents_chain(model, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke({"input": question})
    
    llm_response = response['answer']
    # Ajouter un retour à la ligne après chaque point suivi d'un espace
    llm_response = re.sub(r'(\.)(\s+)', r'.<br>\2', llm_response)

    # Ajouter un retour à la ligne avant et mettre en gras les jours de la semaine
    llm_response = re.sub(r'(Day \d+)', r'<br><strong>\1</strong>', llm_response)

    # Ajouter un retour à la ligne avant et mettre en gras les repas
    llm_response = re.sub(r'(?:Meal|Recipe) \d+:', r'<br><strong>\0</strong>', llm_response)

    return llm_response
