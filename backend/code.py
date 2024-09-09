from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from ipex_llm.langchain.llms import TransformersLLM  # type: ignore
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma  # type: ignore
from langchain.embeddings import HuggingFaceEmbeddings

def load_llm(model_id):
    llm = TransformersLLM.from_model_id(
        model_id=model_id,
        model_kwargs={"max_length": 4000, "trust_remote_code": True},  # Adjust max_length as needed
    )
    return llm

def web_out(urls, model_id):
    loader = WebBaseLoader(urls)
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
    response = summary['result']
    summary_start = response.find("CONCISE SUMMARY:")
    concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()

    return concise_summary

def pdf_out(pdf, model_id):
    loader = PyPDFLoader(pdf, extract_images=False)
    print("PDF LOADED INTO THE LOADER")
    pages = loader.load()
    print("LOADING LLM BELOW")
    
    llm = load_llm(model_id)
    print("SPLITTING TEXT BELOW")
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
