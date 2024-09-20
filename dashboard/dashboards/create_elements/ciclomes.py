import streamlit as st
import pandas as pd
import api


def formulario_create_ciclomes(token, df_ciclomes):
    # Simula um modal com uma chave única
    with st.form(key='form_create_ciclomes'):
        st.write("Preencha os dados para criar um novo CicloMes:")
        
        # Inputs para os campos do CicloMes
        nome = st.text_input('Nome')
        ano = st.number_input('Ano', min_value=2000, max_value=2100, step=1)
        investimento = st.number_input('Investimento', min_value=0.0, format="%.2f")
        dias = st.number_input('Dias', min_value=1, max_value=31, step=1)
        shark = st.number_input('Shark (%)', min_value=0, step=1)
        valor_liquido = st.number_input('Valor Líquido', min_value=0.0, format="%.2f")
        
        # Dados do CicloMes a serem enviados para o backend
        ciclomes_data = {
            "nome": nome,
            "ano": ano,
            "investimento": investimento,
            "dias": dias,
            "shark": float(shark/100),
            "valor_liquido": valor_liquido
        }
                
        submit_button = st.form_submit_button("Criar CicloMes")
        
        if submit_button:
            if nome and ano and investimento and dias:
                if not shark:
                    shark = 0.0
                if not valor_liquido:
                    valor_liquido = 0.0
                resposta = api.create_ciclomes(token, ciclomes_data)
                if "erro" not in resposta:
                    dados_ciclomes = api.get_ciclomeses(token)
                    df_ciclomes = pd.DataFrame(dados_ciclomes)
                    return True, df_ciclomes
                else:
                    st.error(resposta['erro'])
                    return False, df_ciclomes  
            else:
                st.error("Por favor, preencha todos os campos!")
                return False, df_ciclomes 
            
    return False, df_ciclomes  

def create_ciclomes_page(token, dados_ciclomes):
    df_ciclomes = pd.DataFrame(dados_ciclomes)
   
    st.subheader('Criar CicloMes')
    
    resposta_modal, df_ciclomes_novo = formulario_create_ciclomes(token, df_ciclomes)
    
    if resposta_modal:
        st.success("CicloMes criado com sucesso!")
        df_ciclomes = df_ciclomes_novo
