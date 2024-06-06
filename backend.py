import mysql.connector
from mysql.connector import Error
from fastapi import FastAPI
import uvicorn
from functions import Procedimentos
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import json

funcionalidades = Procedimentos()

app = FastAPI()

class Vaga(BaseModel):
    titulo: str
    descricao: str
    salario: float
    localizacao: str
    requisitos: str
    data_publicacao: str
    emprego_id: int
    tipo_filtro: str

# Fazer login
@app.get('/login/{user}/{password}')
async def login(user: str, password: str):
    query = "SELECT * FROM usuario WHERE login = %s;"
    log = funcionalidades.consulta(query, (user,))
    
    if log:
        if password == log[0][2]:  # Assuming the password is in the third column
            return {'Sucesso': 'Efetuado com sucesso!'}
        else:
            return {'Falha': 'Senha incorreta!'}
    else:
        return {'Falha': 'Usuário não encontrado!'}

# Puxar todas as vagas
@app.get('/vagas')
async def vagas():
    try:
        vagas = funcionalidades.consulta('SELECT * FROM vaga;')
        return {'vagas': vagas}
    except Error as e: 
        return {'Erro': str(e)}

# Puxar vagas pelo filtro 
@app.get('/vagas/{tipo}')
async def vagas_f():
    try:
        query = """
        SELECT v.*
        FROM vaga v
        JOIN vaga_filtro vf ON v.id = vf.vaga_id
        JOIN filtro_vaga fv ON vf.filtro_id = fv.id
        WHERE fv.tipo = '{tipo}';
        """
        vagas = funcionalidades.consulta(query)
        return {'vagas': vagas}
    except Error as e: 
        return {'Erro': str(e)}

@app.post('/inserir/vaga/{vaga}')
async def criar_vaga(vaga: Vaga):
    try:
        # Inserir a vaga na tabela `vaga`
        query_vaga = """
        INSERT INTO vaga (titulo, descricao, salario, localizacao, requisitos, data_publicacao, emprego_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        vaga_data = (
            vaga.titulo, vaga.descricao, vaga.salario, vaga.localizacao, 
            vaga.requisitos, vaga.data_publicacao, vaga.emprego_id
        )
        vaga_id = funcionalidades.insert_return_id(query_vaga, vaga_data)
        
        # Obter ou criar filtro correspondente
        query_filtro = "SELECT id FROM filtro_vaga WHERE tipo = %s;"
        filtro = funcionalidades.consulta(query_filtro, (vaga.tipo_filtro,))
        
        if not filtro:
            query_insert_filtro = "INSERT INTO filtro_vaga (tipo) VALUES (%s);"
            filtro_id = funcionalidades.insert_return_id(query_insert_filtro, (vaga.tipo_filtro,))
        else:
            filtro_id = filtro[0][0]
        
        # Associar vaga e filtro na tabela `vaga_filtro`
        query_vaga_filtro = "INSERT INTO vaga_filtro (vaga_id, filtro_id) VALUES (%s, %s);"
        funcionalidades.consulta(query_vaga_filtro, (vaga_id, filtro_id))
        
        return {'Sucesso': 'Vaga inserida com sucesso!'}
    except Error as e:
        return {'Erro': str(e)}

@app.get("/consultar")
# Criado para testar a conexão e fazer consultas específicas
async def conectando():
    query = "INSERT INTO usuario (login, senha) VALUES ('padrao@adm.com', '1234');"
    resultado = funcionalidades.consulta(query)
    try:
        if resultado:
            return JSONResponse(content=jsonable_encoder(resultado))
    except Error as e:
        return {"Erro": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
