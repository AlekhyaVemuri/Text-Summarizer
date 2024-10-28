from transformers import AutoTokenizer
from optimum.intel import OVModelForCausalLM
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from transformers import pipeline
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader

global llm, nectorstore, summ_vectorstore, pdf_vectorstore
summary_template= """Write a concise summary of the following: "{context}" CONCISE SUMMARY: """
query_template="""Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use 10 words maximum and keep the answer as concise as possible in one sentence.
    Always say "thanks for asking!" at the end of the answer.
 
    {context}
 
    Question: {question}
 
    Helpful Answer:"""

def pre_processing(loader):
    """
    
    """
    
    page_data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    all_splits = text_splitter.split_documents(page_data)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)  
    return vectorstore

 
def load_llm(model_id):
    if model_id=="OV Meta LLama 2":
        model_path=<Path to ov_llama_2 folder>
    elif model_id=="OV Qwen 7B Instruct":
        model_path=<Path to ov_qwen7b folder>
    else:
        print("Please select a model!")
    model = OVModelForCausalLM.from_pretrained(model_path , device='GPU')
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    pipe=pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=4000,  
        device=model.device
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    return llm

 
def web_out(urls):
    loader = WebBaseLoader(urls)
    global summ_vectorstore 
    summ_vectorstore = pre_processing(loader)
    prompt = PromptTemplate(
        template=summary_template,
        input_variables=["context", "question"]
    )
 
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=summ_vectorstore.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )
    # qa_chain=pre_processing(loader, load_llm(model_id))
    vectorstore.delete

    question = "Please summarize this book"
    summary = qa_chain({'query': question})
    response = summary['result']
    summary_start = response.find("CONCISE SUMMARY:")
    concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()
 
    return concise_summary
    
 
def url_query(query,model_id):
    prompt = PromptTemplate(
        template=query_template,
        input_variables=["context", "question"]
        )
    reduce_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=summ_vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False
        )
    summary = reduce_chain({'query': query})
    summ_vectorstore.delete
    response = summary['result']
    summary_start = response.find("Helpful Answer:")
    concise_summary = response[summary_start + len("Helpful Answer:"):].strip()
    return concise_summary
 
 
 
def pdf_out(pdf):
    loader = PyPDFLoader(pdf, extract_images=False)
    pdf_vectorstore=pre_processing(loader)
 
    prompt = PromptTemplate(
        template=summary_template,
        input_variables=["context", "question"]
    )
    reduce_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=pdf_vectorstore.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )
    question = "Please summarize the context in one paragraph of 60 words"
    summary = reduce_chain({'query': question})
    vectorstore.delete

    response = summary['result']
    summary_start = response.find("CONCISE SUMMARY:")
    concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()
    # print(concise_summary)
    return concise_summary

def pdf_query(query):
    prompt = PromptTemplate(
        template=query_template,
        input_variables=["context", "question"]
        )
    reduce_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=pdf_vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False
        )
    summary = reduce_chain({'query': query})
    pdf_vectorstore.delete
    response = summary['result']
    summary_start = response.find("Helpful Answer:")
    concise_summary = response[summary_start + len("Helpful Answer:"):].strip()
    return concise_summary
 
