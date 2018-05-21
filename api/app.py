#!flask/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, Response
import pandas as pd


app = Flask(__name__)


def readCSV(file):
    data =  pd.read_csv('../data/' + file, sep =',', names = ['Conferencia', 'Numero_Publicacoes'])
    return data

@app.route('/conferencia.csv')
def get_area_conferencia():
    area = 'chi'
    conferencia = 'INTERACT'
    file = area + '-out-confs.csv'
    data = readCSV(file)
    try:
        return Response(data.to_csv(sep = ',', encoding = 'utf-8', index = False))
    except:
        return "Área ou conferência inválidos"


def main():
    app.run(debug = True, use_reloader = True)


if __name__ == '__main__':
    main()