import json
from flask import Flask, jsonify, render_template, request, redirect, url_for
import pymysql
import pandas as pd
from pandas import DataFrame

app = Flask(__name__, template_folder="templates")

# Configuração do banco de dados
db = pymysql.connect(
    host="localhost",
    user="root",
    password="M@caubas20",
    database="manutenção",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

print("Conexão com banco de dados bem sucedida")


# RENDERIZA A PAGINA HOME
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("/index.html")


# FECHA A PAGINA HOME


# ABRE AQUI AS ROTAS DA PAGINA INDEX
@app.errorhandler(404)
def page_not_found(error):
    return render_template("index.html"), 404


@app.route("/abrir_ordem_de_servico")
def abrir_ordem_de_servico():
    return render_template("abrir_ordem_de_servico.html")


@app.route("/fechar_ordem_de_servico")
def fechar_ordem_de_servico():
    return render_template("fechar_ordem_de_servico.html")


@app.route("/servicos_finalizados")
def servicos_finalizados():
    return render_template("/servicos_finalizados.html")


@app.route("/consultar_no_historico_de_manutencao")
def consulta_no_historico_de_manutencao():
    return render_template("/consultar_historico_de_manutencao.html")


# FECHA AQUI AS ROTAS DA PAGINA INDEX

# ROTAS DA PAGINA DE ABRIR ORDENS DE SERVIÇOS


@app.route("/enviar_para_manutencao", methods=["GET", "POST"])  # Adiciona ao banco de dados funcionando
def enviar_para_manutencao():
    print("enviou para o banco de dados ")
    if request.method == "POST":
        # Obtenha os dados do formulário
        prefixo = request.form.get("prefixo")
        empresa = request.form.get("nome_empresa")
        cliente = request.form.get("nome_do_cliente")
        telefone = request.form.get("numero_telefone")
        data_os = request.form.get("data_de_chegada")
        hora_os = request.form.get("horario_de_chegada")
        servicos = request.form.get("servicos")
        defeitos = request.form.get("defeitos_alegados")

        # Crie um cursor para interagir com o banco de dados
        cursor = db.cursor()

        # Execute o comando SQL para inserir dados na tabela ordens_abertas
        sql = f"INSERT INTO ordens_abertas (prefixo_placa, nome_empresa, nome_cliente, numero_telefone, data_os, hora_os, servicos, defeitos_alegados) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (
            prefixo,
            empresa,
            cliente,
            telefone,
            data_os,
            hora_os,
            servicos,
            defeitos,
        )
        
        try:
            cursor.execute(sql, values)
            db.commit()  # Faça commit para salvar as alterações no banco de dados
            return render_template("/index.html")

        except Exception as e:
            db.rollback()  # Em caso de erro, reverta as alterações
            print(f"Erro ao inserir dados: {e}")

    return render_template("/em_manutencao.html")


# FECHA ROTAS DA PAGINA DE ABRIR ORDENS DE SERVIÇOS

# ABRE AQUI AS ROTAS DA PAGINA HISTORICO DE MANUTENÇÃO


@app.route("/buscar_no_banco_de_dados", methods=["GET"])  ## NÃO FUNCIONOU COMPLETAMENTE
def buscar_no_banco_de_dados():
 
    prefixo_placa = request.form.get("pesquisar_histórico")
    print(prefixo_placa)
    
    sql =  f"SELECT * FROM manutenção.ordens_fechadas WHERE prefixo_placa = '{prefixo_placa}'"
    values = prefixo_placa
    cursor = db.cursor()
    cursor.execute(sql, values)
    resultados = cursor.fetchall
      
    dados = {
                "Nº O.S": [item["Nº_da_os"] for item in resultados],
                "PREFIXO/PLACA": [item["prefixo_placa"] for item in resultados],
                "EMPRESA": [item["nome_empresa"] for item in resultados],
                "CLIENTE": [item["nome_cliente"] for item in resultados],
                "TELEFONE": [item["numero_telefone"] for item in resultados],
                "HORA DE CHEGADA": [item["hora_os"] for item in resultados],
                "DATA DE CHEGADA": [item["data_os"] for item in resultados],
                "SERVIÇOS A EXECUTAR": [item["servicos"] for item in resultados],
                "DEFEITOS ALEGADOS": [item["defeitos_alegados"] for item in resultados]}
    
    df = pd.DataFrame(dados)
    
        
    
    print(df)
    cursor.close()
    return render_template("/resultado_da_consulta.html",tables=[df.to_html(classes="table table-secondary", index=False)],titles=df.columns.values,)
# FECHA AS ROTAS DA PAGINA HISTORICO DE MANUTENÇÃO


@app.route("/em_manutencao", methods=["GET", "POST"])
def lista_atualizada():
    print("enviou para a tabela")
    cursor = db.cursor()
    sql = "SELECT * FROM manutenção.ordens_abertas"

    cursor.execute(sql)
    resultados = cursor.fetchall() 
    
    
    dados = {
        "Nº O.S": [item["Nº_da_os"] for item in resultados],
        "PREFIXO/PLACA": [item["prefixo_placa"] for item in resultados],
        "EMPRESA": [item["nome_empresa"] for item in resultados],
        "CLIENTE": [item["nome_cliente"] for item in resultados],
        "TELEFONE": [item["numero_telefone"] for item in resultados],
        "HORA DE CHEGADA": [item["hora_os"] for item in resultados],
        "DATA DE CHEGADA": [item["data_os"] for item in resultados],
        "SERVIÇOS A EXECUTAR": [item["servicos"] for item in resultados],
        "DEFEITOS ALEGADOS": [item["defeitos_alegados"] for item in resultados],
        
    }
    
    cursor.close()
    # Criar o DataFrame
    df = pd.DataFrame(dados)
    print(df)

    return render_template(
        "/em_manutencao.html",
        tables=[df.to_html(classes="table table-secondary", index=False)],
        titles=df.columns.values,
    )


if __name__ in "__main__":
    app.run(debug=True, port=5500)
