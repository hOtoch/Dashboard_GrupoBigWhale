import streamlit as st
import pandas as pd
import plotly.express as px
import api
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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
        
        with col2:
            plano_filter = st.selectbox("Plano", options=planos_contas, disabled=st.session_state.nome_filter)
        
        with col3:
            meses_filter = st.selectbox("Meses", options=meses_contas, disabled=st.session_state.nome_filter)
        
        if plano_filter != "Todos":
            df_contas = df_contas[df_contas['plano'] == plano_filter]
        
        if meses_filter != "Todos":
            df_contas = df_contas[df_contas['meses'] == meses_filter]
            
        deposito_inicial = df_contas['deposito_inicial'].sum()
        saldo_atual = df_contas['saldo_atual'].sum()
        lucro_liquido = df_contas['liquido'].sum()
        comissao_fundo = df_contas['comissao_fundo'].sum()
        saques = df_contas['saques'].sum()
        margem_lucro = df_contas['margem_lucro'].sum()
                
        col4, col5 = st.columns(2)
    
    
        with col4:
              
            deposito_inicial_formatado = locale.format_string("%.2f", deposito_inicial, grouping=True)
            st.metric(label="Depósito Inicial", value=f"${deposito_inicial_formatado.rstrip('0').rstrip(',')}")
            
          
            lucro_liquido_formatado = locale.format_string("%.2f", lucro_liquido, grouping=True)
            st.metric(label="Lucro Líquido", value=f"${lucro_liquido_formatado.rstrip('0').rstrip(',')}")
            
           
            saques_formatado = locale.format_string("%.2f", saques, grouping=True)
            st.metric(label="Saques", value=f"${saques_formatado.rstrip('0').rstrip(',')}")
                
        with col5:
           
            saldo_atual_formatado = locale.format_string("%.2f", saldo_atual, grouping=True)
            st.metric(label="Saldo Atual", value=f"${saldo_atual_formatado.rstrip('0').rstrip(',')}")
            
           
            operacoes_finalizadas_formatado = locale.format_string("%.2f", df_contas['operacoes_finalizadas'].values[0], grouping=True)
            st.metric(label="Operações Finalizadas", value=f"${operacoes_finalizadas_formatado.rstrip('0').rstrip(',')}")
        
           
            comissao_fundo_formatado = locale.format_string("%.2f", comissao_fundo, grouping=True)
            st.metric(label="Comissão Fundo", value=f"${comissao_fundo_formatado.rstrip('0').rstrip(',')}")
    
       
        fig = px.bar(df_contas, 
                x='nome', 
                y=['deposito_inicial', 'saldo_atual'], 
                barmode='group',
                labels={'value': 'Valores em $', 'variable': 'Tipo'},
                title="Depósito Inicial vs. Saldo Atual")
        
        fig.update_layout(
            xaxis_title="Contas do Usuário",  
            yaxis_title="Valores ($)",  
        )

        st.plotly_chart(fig)
        
        st.metric(label="Margem de Lucro", value=f"${margem_lucro:,.2f}")
            
        col6, col7 = st.columns(2)
        
        with col6:
            fig = px.pie(df_contas, 
                    values='margem_lucro', 
                    names='plano', 
                    hole=0.4,  
                    title='Margem de Lucro por Plano')

        
            fig.update_traces(textinfo='percent+label',  
                            hoverinfo='label+percent+value')  
            
            st.plotly_chart(fig)
            
        with col7:
        
            fig = px.pie(df_contas, 
                    values='margem_lucro', 
                    names='nome', 
                    title='Proporção da Margem de Lucro por Conta'
                    )

            st.plotly_chart(fig)
        
        df_long = df_contas.melt(id_vars='nome', value_vars=['comissao_fundo', 'liquido'], 
                            var_name='Tipo', value_name='Valores')
        
        fig = px.bar(df_long, 
                y='nome', 
                x='Valores', 
                color='Tipo',  
                title='Comissão Fundo e Lucro Líquido por Conta',
                labels={'Valores': 'Valores', 'Tipo': 'Tipo'},
                barmode='group',  
                orientation='h'  
                )


        fig.update_layout(legend_title_text='Tipo', yaxis_title='Contas')
        st.plotly_chart(fig)
    
    else:
        st.error("Nenhuma conta encontrada para este usuário")