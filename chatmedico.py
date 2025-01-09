import streamlit as st
import openai
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os

# Lendo o arquivo CSV contendo o currículo

df = pd.read_csv('Curriculo.csv')

# Configurando chave da API OpenAI
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Inicializando o modelo de linguagem
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0, model='gpt-4o-mini')

# Template para as respostas do chatbot
template = """Você é um especialista Ciencia de Dados. 
Aqui está seu o currículo e uma pergunta feita por um recrutador relacionada. 
Baseie sua resposta no seu currículo apresentado, sendo claro e objetivo.

Currículo: {curriculo}

Pergunta: {pergunta}

Resposta:"""
prompt = PromptTemplate(input_variables=['curriculo', 'pergunta'], template=template)
chain = LLMChain(llm=llm, prompt=prompt)

# Função para gerar resposta com base no currículo
def generate_response(question):
    # Convertendo o DataFrame em um texto estruturado
    curriculo_text = '\n'.join([f"{row['Seção']}: {row['Descrição']}" for _, row in df.iterrows()])
    response = chain.run({'curriculo': curriculo_text, 'pergunta': question})
    return response




