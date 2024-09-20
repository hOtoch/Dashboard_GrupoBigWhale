import streamlit as st
import pandas as pd
import api

def formulario_create_conta(token, df_contas, dados_usuario):
    # Simula um modal com uma chave única
    pd_users = pd.DataFrame(dados_usuario)
    with st.form(key='form_create_conta'):
        st.write("Preencha os dados para criar uma nova Conta:")
        
        nomes_usuarios = pd_users['nome'].values
        
        # Inputs para os campos da Conta
        usuario = st.selectbox('Usuário', nomes_usuarios)  
        nome = st.text_input('Nome')
        deposito_inicial = st.number_input('Depósito Inicial', min_value=0.0, format="%.2f")
        saldo_atual = st.number_input('Saldo Atual', min_value=0.0, format="%.2f")
        plano = st.selectbox('Plano', ['Shrimp','Fish','Whale'])  
        meses = st.selectbox('Meses', ['Mensal','Trimestral','Anual']) 
        comissao = st.number_input('Comissão (%)', min_value=0)
        usuario_id = float(pd_users[pd_users['nome'] == usuario]['id'].values[0])
        
        # Dados da Conta a serem enviados para o backend
        conta_data = {
            "nome": nome,
            "usuario_id": usuario_id,
            "deposito_inicial": deposito_inicial,
            "saldo_atual": saldo_atual,
            "plano": plano,
            "meses": meses,
            "comissao": comissao/100
        }
                
        submit_button = st.form_submit_button("Criar Conta")
        
        if submit_button:
            if nome and plano and meses and comissao:
                if not deposito_inicial:
                    deposito_inicial = 0.0
                if not saldo_atual:
                    saldo_atual = 0.0
                resposta = api.create_conta(token, conta_data)
                if "erro" not in resposta:
                    dados_contas = api.get_contas(token)
                    df_contas = pd.DataFrame(dados_contas)
                    return True, df_contas
                else:
                    st.error(resposta['erro'])
                    return False, df_contas  
            else:
                st.error("Por favor, preencha todos os campos!")
                return False, df_contas 
            
    return False, df_contas  

def create_conta_page(token, dados_contas, dados_usuario):
    df_contas = pd.DataFrame(dados_contas)
   
    st.subheader('Criar Conta')
    
    resposta_modal, df_contas_novo = formulario_create_conta(token, df_contas, dados_usuario)
    
    if resposta_modal:
        st.success("Conta criada com sucesso!")
        df_contas = df_contas_novo
