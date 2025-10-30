# Catarina — Microaprendizagem supervisionada com metodologias ativas e IA

<img width="100%" height="auto" alt="Desenho da Catarina e ao lado o título do projeto: Microaprendizagem supervisionada com metodologias ativas e IA" src="/images/banner.png" />

Descrição
---------
Sistema que gera atividades automaticamente (pipeline em `main.py`) e expõe/visualiza os dados via um aplicativo Flask (`app.py`). Para execução local sem banco real há uma amostra em `data/` (JSON).

Pré-requisitos
--------------
- Python 3.10+
- pip (ou pipenv/poetry)
- Recomenda-se usar um ambiente virtual (venv)

Instalação
---------
1. Clone o repositório:
```bash
git clone https://github.com/RafaelLuizC/hack4edu_IFC
cd hack4edu_IFC
```

2. Crie e ative um venv (Windows):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1    # PowerShell
# ou
.venv\Scripts\activate.bat    # CMD
```

3. Instale dependências:
- Se houver `requirements.txt`:
```bash
pip install -r requirements.txt
```
- Caso não exista, instale ao menos:
```bash
pip install flask python-dotenv
```

Configurar variáveis de ambiente
--------------------------------
O pipeline utiliza modelos de IA via cloud (chave em `.env`). Crie um arquivo `.env` na raiz com a chave necessária, por exemplo:
```
CLOUD_API_KEY=suachaveaqui
```
(Altere o nome da variável conforme o provider usado no código.)

Uso
---
- Rodar o pipeline de geração:
```bash
python main.py
```
Edite `main.py` para informar o caminho/URL do PDF a ser processado, conforme comentário no arquivo.

- Rodar o servidor Flask:
```bash
python app.py
```
Acesse no navegador:
```
http://localhost:5000
```

Banco de dados
------------------------
O repositório contém uma amostra de dados em `data/` usada para execução sem banco real. Para usar um banco real, descomente as linhas 2, 21 e 22 em `app.py` (conforme comentário no arquivo) — confirme se essas linhas ainda correspondem às configurações de banco ao editar.

Dicas e solução de problemas
---------------------------
- Se usar `.env`, garanta que `python-dotenv` esteja instalado (o app deve carregar as variáveis automaticamente).
- Se o Flask não iniciar, verifique permissões da porta 5000 e mensagens no terminal.

Licença
-------
Ver arquivo LICENSE (se houver).