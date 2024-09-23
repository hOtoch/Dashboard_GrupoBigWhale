import streamlit as st
import pandas as pd
import api
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formata_numero(valor):
    if pd.isna(valor): 
        return "-"
    return locale.format_string("%.2f", valor, grouping=True).rstrip('0').rstrip(',')

def exibir_tabela_contas(token, dados_contas, dados_usuario):
    
    if not dados_usuario:
        st.warning("Nenhum usuário cadastrado.")
        return
    
    if not dados_contas:
        st.warning("Nenhuma conta cadastrada.")
        return

    df_contas = pd.DataFrame(dados_contas)
    df_usuarios = pd.DataFrame(dados_usuario)
    
    mapa_usuarios = pd.Series(df_usuarios.nome.values, index=df_usuarios.id).to_dict()
    
    df_contas['nome_usuario'] = df_contas['usuario_id'].map(mapa_usuarios)
    df_contas.drop('inicio', axis=1, inplace=True)
    
    # Formata as colunas numéricas
    colunas_numericas = ['deposito_inicial', 'saldo_atual', 'multiplicador', 'liquido', 
                         'comissao', 'comissao_fundo', 'saques', 'margem_lucro', 'operacoes_finalizadas']
    
    for coluna in colunas_numericas:
        df_contas[coluna] = df_contas[coluna].apply(formata_numero)
    
    # Exibe a tabela de contas no Streamlit
    st.title("Tabela de Contas")
    st.table(df_contas[['nome_usuario', 'nome', 'deposito_inicial', 'saldo_atual', 'multiplicador',
                        'plano', 'meses', 'liquido', 'comissao', 'comissao_fundo', 'saques', 
                        'margem_lucro', 'operacoes_finalizadas']])  # Exibe somente as colunas relevantes
