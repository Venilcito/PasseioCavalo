# COMO RODAR!!!

### 1. Baixando
Tenha o [Python](https://www.python.org/downloads/) instalado (obviamente)

Clone o repositório:
```bash
git clone https://github.com/Venilcito/PasseioCavalo
```

Se não tiver, baixe as bibliotecas:
```bash
pip install asyncio
pip install json
pip install "fastapi[standard]"
```

### 2. Rodando
Abra a pasta do projeto no terminal e rode:
```bash
uvicorn main:app --reload
```