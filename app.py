from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
import tempfile
import pandas as pd

app = Flask(__name__)

DB = 'database.db'


def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/guardar', methods=['POST'])
def guardar():

    data = request.json

    conn = get_conn()

    conn.execute(
        '''
        INSERT INTO base (
            nombre,
            direccion,
            ciudad
        )
        VALUES (?, ?, ?)
        ''',
        (
            data.get('nombre'),
            data.get('direccion'),
            data.get('ciudad')
        )
    )

    conn.commit()
    conn.close()

    return jsonify({'ok': True})


@app.route('/datos')
def datos():

    conn = get_conn()

    rows = conn.execute('SELECT * FROM base').fetchall()

    conn.close()

    resultado = []

    for r in rows:
        resultado.append(dict(r))

    return jsonify(resultado)


@app.route('/exportar')
def exportar():

    conn = get_conn()

    df = pd.read_sql_query(
        'SELECT * FROM base',
        conn
    )

    conn.close()

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix='.xlsx'
    )

    with pd.ExcelWriter(
        temp.name,
        engine='openpyxl'
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name='BASE'
        )

    return send_file(
        temp.name,
        as_attachment=True,
        download_name='BASE_ACTUALIZADA.xlsx'
    )


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 10000))
    )
