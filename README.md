# ROI Investimentos Dashboard

## Acesso
https://roiinvestimentos.com

## Descrição
Este projeto é um sistema de dashboard financeiro desenvolvido para a **ROI Investimentos**, permitindo a visualização de dados e gráficos financeiros de contas dos usuários. Ele possui um sistema de autenticação robusto com integração do Google Authenticator para login seguro e recuperação de senha.

### Principais Tecnologias Utilizadas
- **Backend:** Flask, Flask-JWT-Extended, Flask-Mail
- **Frontend:** Angular, Streamlit (para visualizações dinâmicas de dados)
- **Banco de Dados:** PostgreSQL
- **Autenticação:** JWT, Google Authenticator (TOTP)

## Funcionalidades
- **Autenticação Segura:** Login com autenticação de dois fatores via Google Authenticator.
  
![image](https://github.com/user-attachments/assets/b6130a87-8a1f-497a-a85f-7c469a8f1a61)

![image](https://github.com/user-attachments/assets/86885fa5-53b1-4653-b434-6518d7341271)

![image](https://github.com/user-attachments/assets/15c65376-e50a-4eaa-a21a-371e58350f20)

- **Recuperação de Senha:** Envio de e-mail para redefinição de senha.
- **Dashboard Interativo:** Gráficos e tabelas dinâmicas para visualização de dados financeiros.
  
![image](https://github.com/user-attachments/assets/170dd450-5e9c-4bac-ae9f-86cbb03299bb)

  
- **Controle de Acesso:** Usuários administradores têm acesso a todos os dados; usuários comuns visualizam apenas suas próprias contas.

![image](https://github.com/user-attachments/assets/2c0aaf44-9d5c-4a7d-8162-1034b06d1e17)

- **Filtros Dinâmicos:** Filtragem por nome, plano e meses.

## Autenticação com Google Authenticator
O sistema de autenticação de dois fatores é ativado ao realizar o login com sucesso pela primeira vez. Um QR code será gerado e exibido, que deve ser escaneado pelo aplicativo **Google Authenticator**. A cada login subsequente, será solicitado o código gerado pelo aplicativo.

## Deploy
O deploy foi configurado utilizando NGINX como proxy reverso para rotear as requisições para os diferentes serviços e servidores. A estrutura é organizada da seguinte forma:

1. Backend (Flask): Utilizando o Waitress como servidor de produção.
   
2. Frontend (Angular): Utilizando o comando ng build para gerar a aplicação de frontend e servida como estática pelo NGINX.
   
3. Dashboard (Streamlit): Streamlit é servido em uma porta separada e roteado pelo NGINX.
   
4. Banco de Dados (PostgreSQL): Utilizado como repositório principal para dados de usuários e contas.


