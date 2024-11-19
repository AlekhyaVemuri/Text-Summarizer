#Importing necessary libraries
from transformers import AutoTokenizer, pipeline
from optimum.intel import OVModelForCausalLM
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader

# Prompt Templates for Summarization & QA Bot
summary_template= """Write a concise summary of the following: "{context}" CONCISE SUMMARY: """
query_template="""Use the following pieces of context to answer the question at the end.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Use 10 words maximum and keep the answer as concise as possible in one sentence.
    Always say "thanks for asking!" at the end of the answer.
 
    {context}
 
    Question: {question}
 
    Helpful Answer:"""

#Function created for preprocessing 
def pre_processing(loader):
    """
        This function does the below steps in a sequential order:
        1. Loads page content from the webpage/PDF 
        2. Splits the page data using Recursive Character Text Splitter & creates embeddings using HuggingFace Embeddings
        3. This is further stored into ChromaDB for futher retrieval usage
    """
    try:
        page_data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        all_splits = text_splitter.split_documents(page_data)
        # yield "Creating embeddings..."
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        global vectorstore
        vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)  
        return vectorstore
    except Exception as e:
        print(f"Error while processing Webpage/PDF page content: {e}")
    

 #function created for laoding the LLM
def load_llm(model_id):
    """
        Meta Llama2 & Qwen 7B models are converted to OpenVINO IR Format. This function compiles those converted models on GPU
    """
    if model_id:
        try:
            if model_id=="Meta LLama 2":
                model_path=r"..\models\ov_llama_2"
            elif model_id=="Qwen 7B Instruct":
                model_path=r"..\models\ov_qwen7b"
            model = OVModelForCausalLM.from_pretrained(model_path , device='GPU')
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            pipe=pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=8192,  
                device=model.device
            )
            global llm_model 
            llm_model = HuggingFacePipeline(pipeline=pipe)
            return llm_model
        except Exception as e:
            print(f"Failed to load the model. Please check whether the model_path is correct. \n Error: {e}")

#function created for URL content summarization
def web_out(urls):
    """
        When an end user pastes a URL into the plugin, this function loads the page data & passes into the RetrievalQA chain.
        Post summarization, the summary is returned.
    """
    try:
        loader = WebBaseLoader(urls)
        global summ_vectorstore 
        summ_vectorstore = pre_processing(loader)
        prompt = PromptTemplate(
            template=summary_template,
            input_variables=["context", "question"]
        )
    
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm_model,
            retriever=summ_vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False,
        )
        
        question = "Please summarize the entire book in one paragraph of 100 words"
        summary = qa_chain(question)
        response = summary['result']
        summary_start = response.find("CONCISE SUMMARY:")
        concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()
        print(response)
        return concise_summary
    except Exception as e:
        print(f"Failed to summarize webpage \n Error: {e}")
    
#function created for QnA bot for URL 
def url_query(query):
    """
        Post summarization, end users were given a feature to ask follow-up questions to the BoT.
        This function fetches the query asked by the users, searches an answer from the vectorstore & returns an answer in less than 10 words.
    """
    try:
        prompt = PromptTemplate(
            template=query_template,
            input_variables=["context", "question"]
            )
        reduce_chain = RetrievalQA.from_chain_type(
                llm=llm_model,
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
    except Exception as e:
        print(f"Error in Webpage Summarizer QA BoT: {e}")

#function created for PDF summarization
def pdf_out(pdf):
    """
        When an end-user uploads a PDF into the plugin, this function loads the page data & passes into the RetrievalQA chain.
        Post summarization, the summary is returned.
    """
    try:
        loader = PyPDFLoader(pdf, extract_images=False)
        global pdf_vectorstore
        pdf_vectorstore=pre_processing(loader)
    
        prompt = PromptTemplate(
            template=summary_template,
            input_variables=["context", "question"]
        )
        reduce_chain = RetrievalQA.from_chain_type(
            llm=llm_model,
            retriever=pdf_vectorstore.as_retriever(),
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=False,
        )
        question = "Please summarize the entire book in 100 words."
        summary = reduce_chain({'query': question})

        response = summary['result']
        summary_start = response.find("CONCISE SUMMARY:")
        concise_summary = response[summary_start + len("CONCISE SUMMARY:"):].strip()
        return concise_summary
    except Exception as e:
        print(f"Failed to summarize PDF \n Error: {e}")

#function created for Question Answering bot for PDF
def pdf_query(query):
    """
        Post summarization, end users were given a feature to ask follow-up questions to the BoT.
        This function fetches the query asked by the users, searches an answer from the vectorstore & returns an answer in less than 10 words.
    """
    try:
        prompt = PromptTemplate(
            template=query_template,
            input_variables=["context", "question"]
            )
        reduce_chain = RetrievalQA.from_chain_type(
                llm=llm_model,
                retriever=pdf_vectorstore.as_retriever(),
                chain_type="stuff",
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=False
            )
        summary = reduce_chain({'query': query})
        response = summary['result']
        summary_start = response.find("Helpful Answer:")
        concise_summary = response[summary_start + len("Helpful Answer:"):].strip()
        return concise_summary
    except Exception as e:
        print(f"Error in PDF Summarizer QA BoT: {e}")
