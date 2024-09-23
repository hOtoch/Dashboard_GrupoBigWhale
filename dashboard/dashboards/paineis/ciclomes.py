import streamlit as st
import pandas as pd
import api
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formata_numero(valor):
    if pd.isna(valor):
        return "-"
    return locale.format_string("%.2f", valor, grouping=True).rstrip('0').rstrip(',')

def exibir_tabela_ciclomes(token, dados_ciclomes):
    
    if not dados_ciclomes:
        st.warning("Nenhum Mês cadastrado.")
        return
    
    df_ciclomes = pd.DataFrame(dados_ciclomes)
    
    colunas_numericas_ciclomes = ['atual', 'investimento', 'alcancado', 'projecao', 'porcentagem_alcancado', 'shark', 'valor_liquido']
    
    for coluna in colunas_numericas_ciclomes:
        df_ciclomes[coluna] = df_ciclomes[coluna].apply(formata_numero)
    
    st.title("Tabela de Meses")
    st.table(df_ciclomes[['nome', 'ano', 'atual', 'investimento', 'alcancado', 'projecao', 'porcentagem_alcancado', 'dias', 'shark', 'valor_liquido']]) 

    st.title("Tabela de Dias")
    mes_selecionado_nome = st.selectbox('Selecione um Mês', df_ciclomes['nome'])
    
    mes_selecionado = df_ciclomes[df_ciclomes['nome'] == mes_selecionado_nome].iloc[0]
    
    dados_dias = api.get_dias(token, mes_selecionado['id'])
    
    if dados_dias:
        df_dias = pd.DataFrame(dados_dias)
        df_dias['dia_num'] = range(1, len(df_dias) + 1)
        
        colunas_numericas_dias = ['juros', 'alcancado_dia']
        
        for coluna in colunas_numericas_dias:
            df_dias[coluna] = df_dias[coluna].apply(formata_numero)
        
        st.table(df_dias[['dia_num', 'juros', 'alcancado_dia']])
        
    else:
        st.warning("Não há dias cadastrados para este mês.")
