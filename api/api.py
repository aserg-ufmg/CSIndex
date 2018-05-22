#!flask/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, make_response
import pandas as pd


app = Flask(__name__)


def serveResponse(df, filename):
    response = make_response(df.to_csv(sep = ',', encoding = 'utf-8', index = False, header = False))
    response.headers["Content-Disposition"] = "attachment; filename = " + filename + ".csv"
    response.headers["Content-Type"] = "text/csv"
    return response


# 1: Número de publicações em uma determinada conferência de uma área
@app.route('/numeroPublicacoesConferenciaArea/<area>/<conferencia>')
def numeroPublicacoesConferenciaArea(area, conferencia):
    file = area + '-out-confs.csv'
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = ['Conferencia', 'Numero_Publicacoes'])
    except IOError:
        return "Área ou conferência inválidos"

    response = data[data.Conferencia == conferencia].Numero_Publicacoes
    return serveResponse(response, 'numeroPublicacoesConferenciaArea')


# 2: Número de publicações no conjunto de conferências de uma área
@app.route('/numeroPublicacoesArea/<area>')
def numeroPublicacoesArea(area):
    file = area + '-out-confs.csv'
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = ['Conferencia', 'Numero_Publicacoes'])
    except IOError:
        return "Área inválida"

    response = sum(data.Numero_Publicacoes)
    response = make_response(str(response))
    response.headers["Content-Disposition"] = "attachment; filename = numeroPublicacoesArea.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
    

# 3: Scores de todos os departamentos em uma área
@app.route('/scoreTodosDepartamentosArea/<area>')
def scoreTodosDepartamentosArea(area):
    file = area + '-out-scores.csv'
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = ['Departamento', 'Score'])
    except IOError:
        return "Área inválida"

    return serveResponse(data, 'scoreTodosDepartamentosAreaArea')


# 4: Score de um determinado departamento em uma área.
@app.route('/scoreDepartamentoArea/<area>/<departamento>')
def scoreDepartamentoArea(area, departamento):
    file = area + '-out-scores.csv'
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = ['Departamento', 'Score'])
    except IOError:
        return "Área inválida"

    response = data[data.Departamento == departamento].Score
    return serveResponse(response, 'scoreDepartamentoArea')


# 5: Número de professores que publicam em uma determinada área (organizados por departamentos)
@app.route('/numeroProfessoresAreaAgrupadoDepartamento/<area>')
def numeroProfessoresAreaAgrupadoDepartamento(area):
    file = area + '-out-profs.csv'
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = ['Departamento', 'Numero_Professores'])
    except IOError:
        return "Área inválida"

    return serveResponse(data, 'numeroProfessoresAreaAgrupadoDepartamento')


# 6: Número de professores de um determinado departamento que publicam em uma área
@app.route('/numeroProfessoresDepartamentoArea/<area>/<departamento>')
def numeroProfessoresDepartamentoArea(area, departamento):
    file = area + '-out-profs.csv'
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = ['Departamento', 'Numero_Professores'])
    except IOError:
        return "Área ou departamento inválidos"

    response = data[data.Departamento == departamento].Numero_Professores
    return serveResponse(response, 'numeroProfessoresDepartamentoArea')


# 7: Todos os papers de uma área (ano, título, deptos e autores)
@app.route('/papersArea/<area>')
def papersArea(area):
    file = area + '-out-papers.csv'
    header = ['Ano', 'Conferencia', 'Titulo', 'Departamento', 'Autores', 'Link', 'Top']
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = header)
    except IOError:
        return "Área invalida"

    response = data[['Ano', 'Titulo', 'Departamento', 'Autores']]
    return serveResponse(response, 'papersArea')


# 8: Todos os papers de uma área em um determinado ano
@app.route('/papersAreaAno/<area>/<ano>')
def papersAreaAno(area, ano):
    file = area + '-out-papers.csv'
    header = ['Ano', 'Conferencia', 'Titulo', 'Departamento', 'Autores', 'Link', 'Top']
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = header)
    except IOError:
        return "Área ou ano inválidos"

    response = data[data.Ano == int(ano)]
    return serveResponse(response, 'papersAreaAno')


# 9: Todos os papers de um departamento em uma área
@app.route('/papersAreaDepartamento/<area>/<departamento>')
def papersAreaDepartamento(area, departamento):
    file = area + '-out-papers.csv'
    header = ['Ano', 'Conferencia', 'Titulo', 'Departamento', 'Autores', 'Link', 'Top']
    try:
        data = pd.read_csv('../data/' + file, sep = ',', names = header)
    except IOError:
        return "Área departamento inválidos"

    response = data[data.Departamento == departamento]
    return serveResponse(response, 'papersAreaDepartamento')


#TODO
# 10: Todos os papers de um professor (dado o seu nome)
@app.route('/papersProfessor/<professor>')
def papersProfessor(professor):
    print(professor)


def main():
    app.run(debug = True, use_reloader = True)


if __name__ == '__main__':
    main()