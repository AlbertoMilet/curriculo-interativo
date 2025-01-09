import streamlit as st
import openai
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError 
import gdown

load_dotenv()



SERVICE_ACCOUNT_FILE = 'credentials.json'  
# Baixar o arquivo de credenciais da conta de serviço do Google Drive
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    gdown.download(
        "https://drive.google.com/uc?id=106I47V_fx_bpURD5Dq_crVR2dhdvV6eU",
        SERVICE_ACCOUNT_FILE,
        quiet=False
    )

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def authenticate(service_name):
    """Autentica e retorna o serviço do Google API usando uma conta de serviço"""
    # Caminho para o arquivo de credenciais da conta de serviço
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"Arquivo {SERVICE_ACCOUNT_FILE} não encontrado.")
        return None                             
    else:
        print(f"Arquivo {SERVICE_ACCOUNT_FILE} encontrado.")
    # Autenticar usando a conta de serviço
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    # Desativar o cache de arquivos
    creds = creds.with_quota_project(None)

    # Cria um serviço de API do Google
    service = build(service_name, 'v4', credentials=creds)
    
    return service




# Função para ler dados de uma planilha do Google Sheets
@st.cache_data
def ler_dados_google_sheets(spreadsheet_id, range='A1:U100'):
    """Lê os dados de uma planilha do Google Sheets pelo ID e retorna os dados"""
    service = authenticate('sheets')
    
    
    try:
        # Faz a requisição para obter os dados da planilha
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range
        ).execute()
        values = result.get('values', [])
        print(f"Dados lidos com sucesso da planilha:")
        return values
    except HttpError as error:
        print(f"Erro ao ler os dados da planilha: {error}")
        return None

# Função para localizar a linha no DataFrame dado um telefone

# Lendo o arquivo CSV contendo o currículo

spreadsheet_id_curriculo = os.getenv("SPREADSHEET_ID_CURRICULO")
spreadsheet_id_curriculo = '1k0CQhchFzOQuy9oWYhB0hdDso_N0DazGKnTPJoZjiI8'

dados = ler_dados_google_sheets(spreadsheet_id_curriculo)       
df = pd.DataFrame(dados[1:], columns=dados[0]) 

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




def main():

        
    st.set_page_config(page_title="Curriculo interativo", page_icon="📊", layout="centered", initial_sidebar_state="collapsed")
    with st.sidebar:
        st.title("Sobre este Currículo")
        st.write("""
        Este currículo é uma aplicação interativa desenvolvida com **Streamlit** e integrada ao **OpenAI GPT-4**, utilizando meus dados profissionais e acadêmicos para responder perguntas de forma dinâmica e personalizada.
        """)
        st.write("### Como funciona?")
        st.write("""
        - **Base de dados**: As informações exibidas e utilizadas para gerar respostas são extraídas de um banco de dados atualizado com meu histórico profissional, habilidades e formação acadêmica.
        - **Inteligência Artificial**: O sistema utiliza o modelo **GPT-4** da OpenAI para processar perguntas e gerar respostas claras e contextualizadas, sempre com base nos meus dados.
        - **Interatividade**: Você pode fazer perguntas sobre minhas experiências, habilidades ou projetos, e receber respostas instantâneas.
        """)
        st.write("### Tecnologias utilizadas:")
        st.write("""
        - **Streamlit**: Para criar a interface web interativa.
        - **OpenAI GPT-4**: Para processamento de linguagem natural e geração de respostas.
        - **Google Sheets**: Para armazenar e gerenciar os dados do currículo.
        - **Python**: Para integração de todas as tecnologias e automação dos processos.
        """)
        st.write("### Exemplos de perguntas:")
        st.write("""
        - "Quais são suas principais habilidades em Ciência de Dados?"
        - "Você já trabalhou com machine learning? Quais projetos?"
        - "Quais são suas formações acadêmicas?"
        """)
        st.write("### Observação:")
        st.write("""
        Este currículo é uma réplica do ChatGPT, mas **limitado aos meus dados**. Ele não possui acesso à internet ou a informações externas, garantindo que todas as respostas sejam baseadas exclusivamente no meu histórico profissional e acadêmico.
        """)
        st.write("### Código-fonte:")
        st.write("""
        O código-fonte deste projeto está disponível no [GitHub](https://github.com/seu_usuario/seu_repositorio). Sinta-se à vontade para explorar e contribuir!
        """)
    perfil_file = "perfil.png" 
    url_perfil = os.getenv("URL_PERFIL")
 
    if not os.path.exists(perfil_file):
        gdown.download(url_perfil, perfil_file, quiet=False)  
        
    st.header("Alberto Milet ") 
    st.image(perfil_file, width=150)
    
    st.subheader("Cientista de Dados - Expert em Inteligência Artificial ") 
    pergunta = st.text_area(
    "Digite sua pergunta:",
    placeholder="Estou recrutando para uma vaga de Cientista de Dados Sênior. Quais são suas principais habilidades e experiências na área?",
    height=100
)
    enviar_button = st.button("Enviar")

    if pergunta and enviar_button:
            
        st.write("Aguarde um momento por favor...")
        resposta = generate_response(pergunta)  # Certifique-se de que generate_response está definida e retorna uma resposta
        st.info(resposta)

if __name__ == "__main__":
    main()