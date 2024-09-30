import streamlit as st
import pandas as pd
import plotly.express as px
import api
import locale
import plotly.graph_objects as go

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def deposito_saldo_chart(df_contas):
    st.header("Depósito Inicial x Saldo Atual por Conta")
    st.subheader("Diferença entre o depósito inicial e o saldo atual de cada conta")
    fig = px.bar(df_contas, 
                x='nome', 
                y=['deposito_inicial', 'saldo_atual'], 
                barmode='group',
                labels={'value': 'Valores em $', 'variable': 'Tipo'},
                color_discrete_sequence=["#7C00FE","#F9E400"])
  
        
    fig.update_layout(
        xaxis_title="Contas do Usuário",  
        yaxis_title="Valores ($)",  
        )

    st.plotly_chart(fig)
        
def lucro_plano_chart(df_contas):
    st.header("Margem de Lucro por Plano")
    valores = df_contas['margem_lucro']
    labels = df_contas['plano']

    # Criar o gráfico de rosca com estilo 3D
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=valores,
        hole=0.4,  
        pull=[0.1] * len(valores),  
        marker=dict(
            colors=['#FFAF00', '#7C00FE'],  
            line=dict(color='#ffffff', width=2)  
        )
    )])

    # Configuração do layout
    fig.update_traces(textinfo='percent+value', textfont_size=15)
    fig.update_layout(
        annotations=[dict(text='', x=0.5, y=0.5, font_size=20, showarrow=False)],
        showlegend=True,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)
    

    
def lucro_conta_chart(df_contas):
    st.header("Margem de Lucro x Valor Líquido por Conta")
    st.subheader("Influência da margem de lucro no valor líquido de cada conta")
    fig = px.scatter(df_contas, 
                 x='margem_lucro', 
                 y='liquido', 
                 color='nome',  # Diferenciar cada conta pela cor
                 size='liquido',  # Tamanho das bolhas de acordo com o valor líquido
                 hover_name='nome', 
                 labels={'margem_lucro': 'Margem de Lucro ($)', 'liquido': 'Valor Líquido ($)'}, 
                 color_discrete_sequence= ["#F5004F","#FFAF00","#F9E400","#7C00FE","#FF0080"])

    # Exibir o gráfico no Streamlit
    st.plotly_chart(fig)
    
def comissao_fundo_lucro_chart(df_contas):
    
    st.header("Comissão Fundo x Lucro Líquido por Conta")
    st.subheader("Comparação entre a comissão do fundo e o lucro líquido de cada conta")
    df_long = df_contas.melt(id_vars='nome', value_vars=['comissao_fundo', 'liquido'], 
                            var_name='Tipo', value_name='Valores')
    fig = px.bar(df_long, 
                y='nome', 
                x='Valores', 
                color='Tipo',  
                labels={'Valores': 'Valores', 'Tipo': 'Tipo'},
                barmode='group',  
                orientation='h',
                color_discrete_sequence=["#F5004F","#FFAF00"]  
                )

    fig.update_layout(legend_title_text='Tipo', yaxis_title='Contas')
    st.plotly_chart(fig)
    
def deposito_saques_chart(df_contas):
    st.header("Depósito Inicial x Valor Líquido x Saques por Conta")
    # Definir o índice como o nome das contas para o eixo X
    df_saques = df_contas[['nome', 'deposito_inicial', 'saques', 'liquido']]
    df_saques.set_index('nome', inplace=True)

    # Criar o gráfico de barras com Streamlit
    st.bar_chart(df_saques[['deposito_inicial', 'saques', 'liquido']], color=['#FFAF00', '#F5004F', '#7C00FE'], x_label="Contas", y_label="Valores ($)")
    
def formatar_valores(valor):
    return f"${locale.format_string('%.2f', valor, grouping=True).rstrip('0').rstrip(',')}"
    
def tabela_resumo_contas(df_contas):
    tabela_resumo = df_contas[['nome', 'plano', 'deposito_inicial', 'saques', 'saldo_atual', 'liquido', 'margem_lucro']]

           
    tabela_resumo.columns = ['Nome da Conta', 'Plano', 'Depósito Inicial ($)', 'Saques ($)', 'Saldo Atual ($)', 'Valor Líquido ($)', 'Margem de Lucro ($)']
            
    colunas_a_formatar = ['Depósito Inicial ($)', 'Saques ($)', 'Saldo Atual ($)', 'Valor Líquido ($)', 'Margem de Lucro ($)']
    for col in colunas_a_formatar:
        tabela_resumo[col] = tabela_resumo[col].apply(formatar_valores)
    
    # Remover o índice da exibição
    tabela_resumo = tabela_resumo.reset_index(drop=True)
            
  
    st.header("Tabela Resumo das Contas")
    st.subheader("Resumo dos valores de cada conta")
    st.dataframe(tabela_resumo, use_container_width=True)

def dashboard_user(token):
    
    st.title("Dashboard do Usuário")
    
    if st.session_state['admin']:
        dados_usuario = api.getall_users(token)
        
        if not dados_usuario:
            st.warning("Nenhum usuário cadastrado.")
            return
        
        # st.write(dados_usuario)
        df_usuarios = pd.DataFrame(dados_usuario)
        
        usuario_nome = st.selectbox("Selecione um usuário", df_usuarios['nome'].values)
        usuario_selecionado = df_usuarios[df_usuarios['nome'] == usuario_nome].iloc[0]
        
        
        dados_contas = api.listar_contas_user_admin(token, usuario_selecionado['id'])
    else:
        dados_contas = api.listar_contas_user(token)
        
        if not dados_contas:
            st.warning("Nenhuma conta encontrada para este usuário")
            return
    
    if dados_contas:
    
        planos_contas = set()
        meses_contas = set()
        nomes_contas = set()
        
        for conta in dados_contas:
            planos_contas.add(conta.get('plano'))
            meses_contas.add(conta.get('meses'))
            nomes_contas.add(conta.get('nome'))
            
        planos_contas = ["Todos"] + sorted(list(planos_contas))
        meses_contas = ["Todos"] + sorted(list(meses_contas))
        nomes_contas = ["Todos"] + sorted(list(nomes_contas))
        
        # Usando colunas para alinhar os filtros horizontalmente
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome_filter = st.selectbox("Nome da conta", options=nomes_contas)
        st.session_state['nome_filter'] = False
        
        df_contas = pd.DataFrame(dados_contas)
          
        if nome_filter != "Todos":
            st.session_state['nome_filter'] = True
            df_contas = df_contas[df_contas['nome'] == nome_filter]
            
        deposito_inicial = df_contas['deposito_inicial'].sum()
        saldo_atual = df_contas['saldo_atual'].sum()
        lucro_liquido = df_contas['liquido'].sum()
        comissao_fundo = df_contas['comissao_fundo'].sum()
        saques = df_contas['saques'].sum()
        margem_lucro = df_contas['margem_lucro'].sum()
        
        with col1:
            
            deposito_inicial_formatado = locale.format_string("%.2f", deposito_inicial, grouping=True)
            st.metric(label="Depósito Inicial", value=f"${deposito_inicial_formatado.rstrip('0').rstrip(',')}")
                
            
            saques_formatado = locale.format_string("%.2f", saques, grouping=True)
            st.metric(label="Saques", value=f"${saques_formatado.rstrip('0').rstrip(',')}")
            
            deposito_saldo_chart(df_contas)
            lucro_plano_chart(df_contas)
        
        with col2:
            plano_filter = st.selectbox("Plano", options=planos_contas, disabled=st.session_state.nome_filter)
            saldo_atual_formatado = locale.format_string("%.2f", saldo_atual, grouping=True)
            st.metric(label="Saldo Atual", value=f"${saldo_atual_formatado.rstrip('0').rstrip(',')}")
            
                   
            lucro_liquido_formatado = locale.format_string("%.2f", lucro_liquido, grouping=True)
            st.metric(label="Lucro Líquido", value=f"${lucro_liquido_formatado.rstrip('0').rstrip(',')}")
            
            lucro_conta_chart(df_contas)
            tabela_resumo_contas(df_contas)
            
            
             
        with col3:
            meses_filter = st.selectbox("Meses", options=meses_contas, disabled=st.session_state.nome_filter)
            comissao_fundo_formatado = locale.format_string("%.2f", comissao_fundo, grouping=True)
            st.metric(label="Comissão Fundo", value=f"${comissao_fundo_formatado.rstrip('0').rstrip(',')}")
        
            st.metric(label="Margem de Lucro", value=f"${margem_lucro:,.2f}")
            
            comissao_fundo_lucro_chart(df_contas)
            deposito_saques_chart(df_contas)
        
        if plano_filter != "Todos":
            df_contas = df_contas[df_contas['plano'] == plano_filter]
        
        if meses_filter != "Todos":
            df_contas = df_contas[df_contas['meses'] == meses_filter]
            
        
    else:
        st.error("Nenhuma conta encontrada para este usuário")