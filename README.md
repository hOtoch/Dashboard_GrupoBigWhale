# ROI Investimentos Dashboard

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

- **Recuperação de Senha:** Envio de e-mail para redefinição de senha.
- **Dashboard Interativo:** Gráficos e tabelas dinâmicas para visualização de dados financeiros.
- **Controle de Acesso:** Usuários administradores têm acesso a todos os dados; usuários comuns visualizam apenas suas próprias contas.
- **Filtros Dinâmicos:** Filtragem por nome, plano e meses.

## Autenticação com Google Authenticator
O sistema de autenticação de dois fatores é ativado ao realizar o login com sucesso pela primeira vez. Um QR code será gerado e exibido, que deve ser escaneado pelo aplicativo **Google Authenticator**. A cada login subsequente, será solicitado o código gerado pelo aplicativo.

## Deploy
O deploy é feito utilizando o **Waitress** para o backend, **ng build** para o frontend e configuração do dashboard no servidor.


