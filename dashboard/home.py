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
import locale

load_dotenv()
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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
    st.sidebar.image("assets/logo2.png", use_column_width='always', width=250)
    st.sidebar.divider()
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

def juros_e_alcancado_chart(df_dias):
    st.header("Juros x Valor Alcançado por Dia")
    st.subheader("Análise do valor alcançado de cada dia e seu juros projetado")
    df_dias_indexed = df_dias.set_index('dia_id')
       
    df_chart = df_dias_indexed[['juros', 'alcancado_dia']]
       
    st.line_chart(df_chart, color=["#7C00FE","#F5004F"],x_label="Dia",y_label="Valor ($)")
        
        
def projecao_alcancada_chart(df_filtrado):
    st.header("Projeção x Alcançado")
    st.subheader("Comparação do valor projetado e o valor alcançado até o momento")
    alcancado = df_filtrado['alcancado'].values[0]
    restante_para_projecao = df_filtrado['projecao'].values[0] - alcancado

    # Dados para o gráfico de pizza
    valores = [alcancado, restante_para_projecao]
    labels = ["Alcançado", "Restante da Projeção"]

    # Criando o gráfico de rosca com aparência 3D
    fig_pizza_3d = go.Figure(data=[go.Pie(
        labels=labels,
        values=valores,
        hole=0.4,  
        pull=[0.1, 0],  
        marker=dict(
            colors=['#F9E400', '#F5004F'], 
            line=dict(color='#000000', width=2) 
        )
    )])

    # Configuração para simular o efeito 3D no layout
    fig_pizza_3d.update_traces(textinfo='percent+value', textfont_size=15)
    fig_pizza_3d.update_layout(
        annotations=[dict(text='',x=0.5, y=0.5, font_size=20, showarrow=False)],
        showlegend=True,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    st.plotly_chart(fig_pizza_3d)
        
        
def liquido_chart(df_ciclomeses, df_contas):
    
    st.header("Valor Líquido por Plano")
    st.subheader("Qual plano possui maior valor líquido?")
    df_agrupado = df_contas.groupby('plano')['liquido'].sum().reset_index()
    
    df_chart = df_agrupado.set_index('plano')
    
    st.bar_chart(df_chart, height=400, horizontal=True, use_container_width=True, color=["#FFAF00"], x_label="Valor ($)", y_label="Plano")
    
  
        
def investido_chart(df_ciclomeses):
    st.header("Investimento x Alcançado por Mês")
    st.subheader("Comparação do valor investido e o valor alcançado por mês")
    fig = px.area(df_ciclomeses.reset_index(), x='nome', y=['investimento', 'alcancado'],
              labels={'value': 'Valor ($)', 'variable': 'Métricas'},
              color_discrete_sequence=['#7C00FE', '#F9E400'])
    
    st.plotly_chart(fig)

        
        
def dashboard_padrao(token, dados_ciclomeses, dados_contas):
    
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
    
    df_contas = pd.DataFrame(dados_contas)

    
    
    
    

            
            
    col1,col2,col3 = st.columns([1,1,1])
    
    with col1:
        try:
            dados_dias = api.get_dias(token, df_filtrado['id'].values[0])
            df_dias = pd.DataFrame(dados_dias)
            df_dias = df_dias.sort_values(by="id", ascending=True)
            df_dias['dia_id'] = range(1, len(df_dias) + 1)
            juros_e_alcancado_chart(df_dias)
            
        except Exception as e:
            st.error("O mês selecionado não possui dados dos dias relacionados a ele")
            
        projecao_alcancada_chart(df_filtrado)
        
    with col2: 
        liquido_chart(df_ciclomeses, df_contas)
        investido_chart(df_ciclomeses)
        
    with col3:
        mes_atual = df_filtrado['id'].values[0]
        mes_atual_index = df_ciclomeses[df_ciclomeses['id'] == mes_atual].index[0]
          
        
        if mes_atual_index > 0:  # Verifica se há um mês anterior
            mes_anterior = df_ciclomeses.iloc[mes_atual_index - 1]
            delta_investimento = df_filtrado['investimento'].values[0] - mes_anterior['investimento']
            delta_projecao = df_filtrado['projecao'].values[0] - mes_anterior['projecao']
            delta_alcancado = df_filtrado['alcancado'].values[0] - mes_anterior['alcancado']
        else:
            delta_investimento = delta_projecao = delta_alcancado = 0
        
        investimento_formatado = locale.format_string("%.2f", df_filtrado['investimento'].values[0], grouping=True)
        st.metric(label='Investimento',value=f"${investimento_formatado.rstrip('0').rstrip(',')}", delta=f"${delta_investimento:,.2f}")
        
        projecao_formatada = locale.format_string("%.2f", df_filtrado['projecao'].values[0], grouping=True)
        st.metric(label='Projeção',value=f"${projecao_formatada.rstrip('0').rstrip(',')}", delta=f"${delta_projecao:,.2f}")
    
        alcancado_formatado = locale.format_string("%.2f", df_filtrado['alcancado'].values[0], grouping=True)
        st.metric(label='Alcançado',value=f"${alcancado_formatado.rstrip('0').rstrip(',')}", delta=f"${delta_alcancado:,.2f}")
        
        porcentagem_alcancada = df_filtrado['porcentagem_alcancado'].values[0] * 100
        porcentagem_formatada = locale.format_string("%.2f", porcentagem_alcancada, grouping=True)
        
        
        col4,col5,col6 = st.columns([1,1,1])
        
        with col4:
            with st.container(border=True):
                st.metric(label="Porcentagem Alcançada", value=f"{porcentagem_formatada.rstrip('0').rstrip(',')}%")
        with col5:
            with st.container(border=True):
                st.metric(label="Shark - Dia", value=f"{shark_porcentagem}%")
        with col6:
            with st.container(border=True):
                st.metric(label="Dias", value=df_filtrado['dias'].values[0])
           
       

def main():
    token = get_params()

    st.set_page_config(
        page_title="Dashboard",  # Defina o título que aparecerá na aba do navegador
        page_icon="./assets/logo.png",  # Você pode usar um emoji, URL de uma imagem ou caminho para um arquivo de imagem local
        layout="wide"
    )
    estilo_css = """
        
		<style>
       
  
        [data-testid="stHeader"]{
            background-color: rgba(0,0,0,0);
        }
        [data-testid="stSidebarContent"]{
            color: white;
        }
      
        
        [data-testid="stSidebarContent"] p {
            color: white;
        }
        
        h1,p{
            color: white;
        }
        
        h2 {
            color: white;
            font-size: 1.5em;
        }
        
        h3 {
            color: white;
            font-size: 0.8em;
        }
        
        
        [data-testid="stMetricValue"] {
           color: #FFAF00;
           font-weight: bold;
        }

        
        [data-testid="stTable"] {
            padding-top: 12px;
            padding-bottom: 0px;
        }

		</style>	
		
        """

    st.markdown(estilo_css, unsafe_allow_html=True)
    
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
        
            
            
            if not 'admin' in st.session_state:
                st.session_state['admin'] = False
            
            if dados_user['tipo_usuario'] == "admin":
                st.session_state['admin'] = True
            
            dashboard_selecionado = side_bar(token, dados_user)
            
            if dashboard_selecionado == "🏠 Dashboard Inicial":
                dashboard_padrao(token, dados_ciclomeses, dados_contas)
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
    

   
        
    
    
    
    