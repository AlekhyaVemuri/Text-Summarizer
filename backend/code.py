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

summary_template= """Write a concise summary of the following: "{context}" CONCISE SUMMARY: """
query_template="""Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use 10 words maximum and keep the answer as concise as possible in one sentence.
    Always say "thanks for asking!" at the end of the answer.
 
    {context}
 
    Question: {question}
 
    Helpful Answer:"""

def pre_processing(loader):
    page_data = loader.load()
   
    # llm = load_llm(model_id)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    all_splits = text_splitter.split_documents(page_data)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)
   
    # prompt_template = """Write a concise summary of the following: "{context}" CONCISE SUMMARY: """
    
    return vectorstore

 
def load_llm(model_id):
    if model_id=="ov_llama_2":
        model_path=r"<path of the OV Llama model>"
    else:
        model_path=r"<path of the OV Qwen model>"
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

 
def web_out(urls, model_id):
    loader = WebBaseLoader(urls)
    global w_llm
    w_llm=load_llm(model_id)
    global summ_vectorstore 
    summ_vectorstore = pre_processing(loader)
    prompt = PromptTemplate(
        template=summary_template,
        input_variables=["context", "question"]
    )
 
    qa_chain = RetrievalQA.from_chain_type(
        llm=w_llm,
        retriever=summ_vectorstore.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )     
    question = "Please summarize the context in one paragraph of 100 words"
    summary = qa_chain({'query': question})
    response = summary['result']
    summary_start = response.find("CONCISE SUMMARY:")
    concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()
 
    return concise_summary
 
def url_query(query,model_id):
    wq_llm = w_llm
    q_vectorstore=summ_vectorstore
        
    prompt = PromptTemplate(
        template=query_template,
        input_variables=["context", "question"]
        )
    reduce_chain = RetrievalQA.from_chain_type(
            llm=wq_llm,
            retriever=q_vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False
        )
    summary = reduce_chain({'query': query})
    response = summary['result']
    summary_start = response.find("Helpful Answer:")
    concise_summary = response[summary_start + len("Helpful Answer:"):].strip()
    return concise_summary
  
def pdf_out(pdf, model_id):
    loader = PyPDFLoader(pdf, extract_images=False)
    global pdf_vectorstore, p_llm
    pdf_vectorstore=pre_processing(loader)
    p_llm = load_llm(model_id)
 
    prompt = PromptTemplate(
        template=summary_template,
        input_variables=["context", "question"]
    )
    reduce_chain = RetrievalQA.from_chain_type(
        llm=p_llm,
        retriever=pdf_vectorstore.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )
    question = "Please summarize the context in one paragraph of 100 words"
    summary = reduce_chain({'query': question})
    response = summary['result']
    summary_start = response.find("CONCISE SUMMARY:")
    concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()
    return concise_summary

def pdf_query(query,model_id):
    pq_llm = p_llm
    vectorstore = pdf_vectorstore
    prompt = PromptTemplate(
        template=query_template,
        input_variables=["context", "question"]
        )
    reduce_chain = RetrievalQA.from_chain_type(
            llm=pq_llm,
            retriever=vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False
        )
    summary = reduce_chain({'query': query})
    response = summary['result']
    summary_start = response.find("Helpful Answer:")
    concise_summary = response[summary_start + len("Helpful Answer:"):].strip()
    return concise_summary
 
