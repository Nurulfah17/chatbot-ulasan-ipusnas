# -*- coding: utf-8 -*-
"""predictor

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SCl8Hq3zE5zHv_u5oujA2L2JzPOLIt9Y
"""
import torch
import transformers
import langchain
import numpy as np
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def load_quantized_model(model_name):
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_4bit=True,
        torch_dtype=torch.bfloat16,
        quantization_config=bnb_config
    )
    return model

def initialize_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.bos_token_id = 1
    return tokenizer

def setup_qa_chain():
    # Specify model huggingface model name
    model_name = "anakin87/zephyr-7b-alpha-sharded"

    # Load quantized model
    model = load_quantized_model(model_name)

    # Initialize tokenizer
    tokenizer = initialize_tokenizer(model_name)

    # Specify stop token ids
    stop_token_ids = [0]

    # Load data from CSV
    loader = CSVLoader(file_path='https://drive.google.com/uc?id=1fTBrRiyd24I7334L7BdZY5wYpb85zhbm&confirm=t', encoding="unicode_escape", csv_args={'delimiter': ','})
    docs = loader.load()

    # Split documents
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(docs)

    # Specify embedding model (using Hugging Face sentence transformer)
    embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device": "cuda"}
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name, model_kwargs=model_kwargs)

    # Embed document chunks
    vectordb = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory="chroma_db2")

    # Specify the retriever
    retriever = vectordb.as_retriever()

    # Specify generative language model (LLM)
    pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        use_cache=True,
        device_map="auto",
        max_length=700,
        do_sample=True,
        top_k=2,
        temperature=0.3,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
    )

    # Specify the LLM
    llm = HuggingFacePipeline(pipeline=pipeline)

    # Build chain
    template = """
    Selalu ramah dan persuasif. Gunakan emoticon bila diperlukan.
    Berikan jawaban yang komprehensif dan padat.
    Jangan berikan jawaban jika keyword pada pertanyaan di luar ipusnas.
    {context}
    Question: {question}
    Helpful Answer:
    """

    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"], template=template)

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        chain_type_kwargs={
            "prompt": QA_CHAIN_PROMPT,
        }
    )

    return qa_chain

def chat_with_qa_chain(qa_chain, input):
    result = qa_chain(input)
    print(result['result'])
    return result
