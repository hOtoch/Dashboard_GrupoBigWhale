import streamlit as st
import streamlit.components.v1 as components
import api
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import jwt
from dotenv import load_dotenv
from dashboards.dashboard_user import dashboard_user
from dashboards.dashboard_admin import dashboard_admin
import base64

load_dotenv()

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


SECRET_KEY = os.getenv('JWT_SECRET_KEY')

if not SECRET_KEY:
    st.error("Chave secreta JWT não encontrada. Verifique as variáveis de ambiente.")

def verificar_token(token):
    try:
        # Decodifica o token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload  # Retorna o payload se for válido
    except jwt.ExpiredSignatureError:
        st.error("Token expirado. Faça login novamente.")
        return None
    except jwt.InvalidTokenError:
        st.error("Token inválido. Faça login novamente.")
        return None
    
def side_bar(token,dados_user):
    st.sidebar.write(":material/account_circle:", dados_user['nome'])
                
    st.sidebar.title("Menu")
    
    if st.session_state['admin']:
        dashboard_selecionado = st.sidebar.selectbox("Escolha um dashboard",
                                                    ("🏠 Dashboard Inicial","📊 Dashboard do Usuário","🛠 Dasboard do Administrador"),
                                                    key="sidebar_dashboard_home_selectbox")
        
    else:
        dashboard_selecionado = st.sidebar.selectbox("Escolha um dashboard",
                                                    ("🏠 Dashboard Inicial","📊 Dashboard do Usuário"),
                                                    key="sidebar_dashboard_home_selectbox")
    
    st.session_state['dashboard_selecionado'] = dashboard_selecionado
    
    
    
    image_position = """
                    <style>
                        [data-testid="stImageContainer"]{
                            width: 20px;
                            
                        }
                    </style>
    """
    st.markdown(image_position, unsafe_allow_html=True)
    
    return dashboard_selecionado
   

def get_params():
    query_string = st.query_params
    token = query_string.get('token')
    return token

def dashboard_padrao(token, dados_ciclomeses):
    
    st.title("Dashboard Inicial")
    
    if not dados_ciclomeses:
        st.info("Não há dados de meses disponíveis para exibir.")
        return

    df_ciclomeses = pd.DataFrame(dados_ciclomeses)
    

    df_ciclomeses['mes_ano'] = df_ciclomeses['nome'] + ' de ' + df_ciclomeses['ano'].astype(str)
    df_ciclomeses = df_ciclomeses.sort_values(by="id", ascending=True)

    mes_selecionado = st.selectbox('Selecione um mês:', df_ciclomeses['mes_ano'])

    df_filtrado = df_ciclomeses[df_ciclomeses['nome'] == mes_selecionado.split(sep=' ')[0]]
    shark_porcentagem = (df_filtrado['shark'].values[0]) * 100


    col1, col2, col3 = st.columns([2,1,1])

    # Exibindo as métricas lado a lado
    with col1:
        st.metric(label="Investimento", value=f"${df_filtrado['investimento'].values[0]:,.2f}")
        st.metric(label="Alcançado", value=f"${df_filtrado['alcancado'].values[0]:,.2f}")
    with col2:
        st.metric(label="Dias", value=df_filtrado['dias'].values[0])
        st.metric(label="Projeção", value=f"${df_filtrado['projecao'].values[0]:,.2f}")
    with col3:
        st.metric(label="Shark - Dia", value=f"{shark_porcentagem}%")
        porcentagem_alcancada = (df_filtrado['porcentagem_alcancado'].values[0]) * 100
        st.metric(label="Porcentagem Alcançada", value=f"{porcentagem_alcancada}%")
        
    try:
        dados_dias = api.get_dias(token, df_filtrado['id'].values[0])
        df_dias = pd.DataFrame(dados_dias)
        df_dias = df_dias.sort_values(by="id", ascending=True)
        df_dias['dia_id'] = range(1, len(df_dias) + 1)
        
        fig = px.line(df_dias, x="dia_id", y=["juros", "alcancado_dia"], 
                labels={"value": "Valores", "variable": "Métricas"},
                title="Juros e Valor Alcançado por Dia")

        st.plotly_chart(fig)
    except Exception as e:
        st.error("O mês selecionado não possui dados dos dias relacionados a ele")
        
    alcancado = df_filtrado['alcancado'].values[0]
    restante_para_projecao = df_filtrado['projecao'].values[0] - alcancado

    # Dados para o gráfico de pizza
    valores = [alcancado, restante_para_projecao]
    labels = ["Alcançado", "Restante da Projeção"]

    # Criando o gráfico de pizza
    fig_pizza = px.pie(
        names=labels,
        values=valores,
        title="Progresso da Projeção Alcançada",
        hole=0.4  # Torna o gráfico um "donut"
    )

    fig_pizza.update_traces(
        textinfo='percent+value',  # Exibe label, porcentagem e valor
        textfont_size=15,                # Tamanho da fonte dos valores
        hoverinfo='label+percent+value'  # Informações ao passar o mouse
    )

    # Exibir o gráfico de pizza
    st.plotly_chart(fig_pizza)
        
        
    fig = px.bar(df_ciclomeses, x="mes_ano", y="investimento", title="Valor Investido por Mês")
    st.plotly_chart(fig)
        

    fig_waterfall = go.Figure(go.Waterfall(
        name="Valor Líquido", 
        orientation="v",
        x=df_ciclomeses['mes_ano'],  # Eixo X com meses
        y=df_ciclomeses['valor_liquido'],  # Valores líquidos
        textposition="outside",
        text=df_ciclomeses['valor_liquido'].map(lambda x: f"${x:,.2f}"),
        connector={"line":{"color":"rgb(63, 63, 63)"}},
    ))

    fig_waterfall.update_layout(
        title="Valores Líquidos por Mês",
        showlegend=False
    )

    # Exibir o gráfico de cascata
    st.plotly_chart(fig_waterfall)

def main():
    token = get_params()

    st.set_page_config(
        page_title="Dashboard",  # Defina o título que aparecerá na aba do navegador
        page_icon="./assets/logo.png",  # Você pode usar um emoji, URL de uma imagem ou caminho para um arquivo de imagem local
        layout="wide"
    )
    video_html = """
    
        <video autoplay muted loop id="myVideo">
		  <source src="https://videos.pexels.com/video-files/28464229/12391209_1920_1080_30fps.mp4">
		  Your browser does not support HTML5 video.
		</video>
		<style>
  
        [data-testid="stHeader"]{
            background-color: rgba(0,0,0,0);
        }
        [data-testid="stSidebarContent"]{
            background-color: #444444;
            color: white;
        }
        
        [data-testid="stMetricValue"] {
            background-color: white;
            border-radius: 10px;
            padding: 0px;
        }

        
        [data-testid="stHeadingWithActionElements"] h1{
            color: black;
        }
        
        [data-testid="stTable"] {
            background-color: rgba(255,255,255,0.7);
            border-radius: 15px;
            padding-top: 12px;
            padding-bottom: 0px;
            box-shadow: 0 4px 6px 0 rgba(0, 0, 0,0.7);
        }
        
        
        [data-testid="stMarkdownContainer"] {
            color: black;
        }

		#myVideo {
		  position: fixed;
		  right: 0;
		  bottom: -50px;
		  min-width: 100%; 
		  min-height: 100%;
		}
    

		</style>	
		
        """

    st.markdown(video_html, unsafe_allow_html=True)
    
    if token:
        payload = verificar_token(token)
        user_id = payload['sub']
        if payload:
            try:
                dados_user = api.get_user(token, user_id)      
                       
            except Exception as e:
                st.error("Erro ao processar os dados do usuário.")
                st.error(str(e))
                
            dados_ciclomeses = api.get_ciclomeses(token)
            dados_contas = api.get_contas(token)
            
            st.sidebar.image("assets/logo2.png", use_column_width='always', width=250)
            
            st.header(f"Bem-vindo, {dados_user['nome']}!")
            
            if not 'admin' in st.session_state:
                st.session_state['admin'] = False
            
            if dados_user['tipo_usuario'] == "admin":
                st.session_state['admin'] = True
            
            dashboard_selecionado = side_bar(token, dados_user)
            
            if dashboard_selecionado == "🏠 Dashboard Inicial":
                dashboard_padrao(token, dados_ciclomeses)
            elif dashboard_selecionado == "📊 Dashboard do Usuário":
                dashboard_user(token)
            elif dashboard_selecionado == "🛠 Dasboard do Administrador":
                dados_usuarios = api.getall_users(token)
                dashboard_admin(token, dados_usuarios, dados_ciclomeses, dados_contas)
            
        else:
            st.error("Autenticação falhou. Faça login novamente.")
    else:
        st.error("Acesso não autorizado. Por favor, faça login.")
        
    
    
if __name__ == "__main__":
    main()
    

   
        
    
    
    
    