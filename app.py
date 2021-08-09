from flask import Flask, request
from flask import render_template
import sqlite3
import csv
import os
from pycpfcnpj import cpfcnpj
import pandas as pd

DATABASE = "database.db"
dados_csv = "dados.csv"

app = Flask(__name__)

def importar_csv(dados):
    with open(dados, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=';')
        rows_itens = [tuple(row) for row in rows]
        lista = []
        for i in rows_itens[1:]:
            lista.append((i[0]+i[1]+i[2]+i[3], i[0], i[1], i[2], i[3], i[4], i[5], i[6],\
            i[7], i[8], i[9], i[10], i[11], i[12], i[13], i[14], i[15],\
            i[16], i[17], i[18], i[19]))

        return lista

def criar_tabela():
    sql_create_table = """ 
        CREATE TABLE IF NOT EXISTS data (
            CONTA_CONCAT text,
            AGENCIA text,
            OP text,
            CONTA text,
            DV text,
            CPF_CNPJ text,
            CPF_CNPJ2 text,
            CPF_CNPJ3 text,
            CPF_CNPJ4 text,
            ABERTURA text,
            ultimoCheque text,
            ultimaMovimentacao text,
            TC text,
            ultimaMovEspontanea text,
            CARTEIRA text,
            nome1 text,
            nome2 text,
            nome3 text,
            nome4 text,
            contaBloqueada text,
            contaCaCl text
    ); """

    return sql_create_table

def init():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute(criar_tabela())

    if os.path.exists(dados_csv):
        count = cur.execute("SELECT COUNT(*) FROM data")
        number = count.fetchone()[0]

        if number == 0:
            linhas = importar_csv(dados_csv)
            cur.executemany("INSERT INTO data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", linhas)
        
        con.commit()

def procurar(parametro):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    query = """SELECT * FROM data WHERE 
        CPF_CNPJ = {valor} OR
        CPF_CNPJ2 = {valor} OR
        CPF_CNPJ3 = {valor} OR
        CPF_CNPJ4 = {valor}
    """.format(valor = parametro)

    cur.execute(query)
    registros = cur.fetchall()

    return registros

def quantidade_registros(registros):
    qtd_registros = len(registros)

    if qtd_registros == 1:
        info = '1 registro encontrado'
    elif qtd_registros > 1 or qtd_registros == 0:
        info = '{} registros encontrados'.format(qtd_registros)
    
    return info


def retirar_null(registros):
    registro_editado = []
    for registro in registros:
        lista = []
        for item in registro:
            if item != 'NULL':
                lista.append(item)
            else:
                lista.append('')
        registro_editado.append(lista)

    return registro_editado

@app.route("/")
def index():
    init()
    
    return render_template('index.html')

@app.route("/grafico", methods=['GET'])
def grafico():
    dados = pd.read_csv(dados_csv, delimiter=';')
    sf = dados[dados.contaBloqueada == 1].CARTEIRA.value_counts() / len(dados) * 100
    df = pd.DataFrame({'carteira':sf.index, 'conta_bloqueada_fi':sf.values})

    lista = df.values.tolist()
    key = [i[0] for i in lista]
    data = [i[1] for i in lista]

    return render_template('grafico.html', label=key, data=data)

@app.route("/ajax/search/", methods=['GET'])
def search():
    parametro = request.args.get('parametro')
    tipo = request.args.get('tipo')

    parametro_cpf = f"{parametro:0>11}"
    parametro_cnpj = f"{parametro:0>14}"
    
    if tipo == 'CPF/CNPJ':
        cpfValidar = cpfcnpj.validate(parametro_cpf)
        cnpjValidar = cpfcnpj.validate(parametro_cnpj)

        if cpfValidar == True:
            registros = procurar(parametro)
            info = quantidade_registros(registros)
            registro_editado = retirar_null(registros)
            
            return render_template('table.html', registros=registro_editado, qtd_registros=info)
        
        if cnpjValidar == True:
            registros = procurar(parametro)
            info = quantidade_registros(registros)
            registro_editado = retirar_null(registros)

            return render_template('table.html', registros=registro_editado, qtd_registros=info)

        if cpfValidar == False and cnpjValidar == False:
            msg_erro = 'CPF/CNPJ inválido'
            return render_template('erro.html', msg_erro=msg_erro)

    else:
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        query = "SELECT * FROM data WHERE conta_concat = {}".format(parametro)
        cur.execute(query)
        registros = cur.fetchall()
        info = quantidade_registros(registros)
        registro_editado = retirar_null(registros)

        return render_template('table.html', registros=registro_editado, qtd_registros=info)

if __name__ == '__main__':
    app.run(debug=True)