# COMO RODAR O PROJETO

### 1. Baixando
Tenha o [Python](https://www.python.org/downloads/) instalado

Clone o repositório:
```bash
git clone https://github.com/Venilcito/PasseioCavalo
```

Caso não tenha por padrão, baixe as bibliotecas:
```bash
pip install asyncio
pip install json
pip install "fastapi[standard]"
```

### 2. Rodando
Abra a pasta do projeto no terminal e execute:
```bash
uvicorn main:app --reload
```