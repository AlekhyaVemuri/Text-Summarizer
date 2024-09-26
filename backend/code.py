# from openvino.runtime import Core, get_version
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
# import pathlib

def load_llm(model_id):
    if model_id=="ov_llama_2":
        model_path=r"C:\DIYA\SummarizerPluginV2F_V2part2\SummarizerPluginV2F_V2part2\ov_llama_2"
    else:
        model_path=r"C:\DIYA\SummarizerPluginV2F_V2part2\SummarizerPluginV2F_V2part2\ov_qwen7b"
    model = OVModelForCausalLM.from_pretrained(model_path , device='GPU')
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    pipe=pipeline(
        "text-generation", 
        model=model, 
        tokenizer=tokenizer,
        max_length=4000,
        truncation=True,  
        device=model.device
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    return llm

def web_out(urls, model_id):
    loader = WebBaseLoader(urls)
    global page_data
    page_data = loader.load()
    
    llm = load_llm(model_id)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    all_splits = text_splitter.split_documents(page_data)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)
    
    prompt_template = """Write a concise summary of the following: "{context}" CONCISE SUMMARY: """
    prompt = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(), 
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )
    
    question = "Please summarize this book"
    summary = qa_chain({'query': question})
    print(summary)
    response = summary['result']
    summary_start = response.find("CONCISE SUMMARY:")
    concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()

    return concise_summary

def url_query(query, model_id):
    pages_query1= page_data
    llm = load_llm(model_id)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=100,
                                               length_function=len,
                                               add_start_index=True)

    chunks=text_splitter.split_documents(pages_query1)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    template = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use 10 words maximum and keep the answer as concise as possible in one sentence.
    Always say "thanks for asking!" at the end of the answer.

    {context}

    Question: {question}

    Helpful Answer:"""
    prompt = PromptTemplate(
        template=template, 
        input_variables=["context", "question"]
        )
    #global reduce_chain
    reduce_chain = RetrievalQA.from_chain_type(
            llm=llm,
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



def pdf_out(pdf, model_id):
    loader = PyPDFLoader(pdf, extract_images=False)
    global pages
    pages = loader.load()
    llm = load_llm(model_id)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    chunks = text_splitter.split_documents(pages)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    print("PASSING FROM CHROMA DB TO PROMPT")
    reduce_template = """Write a concise summary of the following: "{context}" CONCISE SUMMARY: """
    prompt = PromptTemplate(
        template=reduce_template, 
        input_variables=["context", "question"]
    )
    print("Reduce_chain starts here")
    reduce_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(), 
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=False,
    )
    print("Passing a question to chain")
    question = "Please summarize this book"
    summary = reduce_chain({'query': question})
    response = summary['result']
    summary_start = response.find("CONCISE SUMMARY:")
    concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()

    return concise_summary
def pdf_query(query,model_id):
    pages_query= pages
    llm = load_llm(model_id)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=100,
                                               length_function=len,
                                               add_start_index=True)

    chunks=text_splitter.split_documents(pages_query)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    template = """Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use 10 words maximum and keep the answer as concise as possible in one sentence.
    Always say "thanks for asking!" at the end of the answer.

    {context}

    Question: {question}

    Helpful Answer:"""
    prompt = PromptTemplate(
        template=template, 
        input_variables=["context", "question"]
        )
    #global reduce_chain
    reduce_chain = RetrievalQA.from_chain_type(
            llm=llm,
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
