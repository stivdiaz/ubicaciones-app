from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import os

app = Flask(__name__)

DB_PATH = 'database.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar')
def buscar():

    doc = request.args.get('doc', '').strip()

    conn = get_conn()

    query = """
        SELECT rowid as rid, *
        FROM base
        WHERE CAST([Doc. Identidad] AS TEXT) LIKE ?
        LIMIT 100
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[f'%{doc}%']
    )

    conn.close()

    return jsonify(
        df.fillna('').to_dict(orient='records')
    )

@app.route('/pisos')
def pisos():

    conn = get_conn()

    query = """
        SELECT DISTINCT [PISO]
        FROM base
        WHERE [PISO] IS NOT NULL
          AND TRIM([PISO]) <> ''
        ORDER BY [PISO]
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    pisos = (
        df['PISO']
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return jsonify(pisos)

@app.route('/ubicaciones')
def ubicaciones():

    piso = request.args.get('piso', '').strip()

    conn = get_conn()

    query = """
        SELECT DISTINCT [UBICACIÓN DETALLADA]
        FROM base
        WHERE [PISO] = ?
          AND [UBICACIÓN DETALLADA] IS NOT NULL
          AND TRIM([UBICACIÓN DETALLADA]) <> ''
        ORDER BY [UBICACIÓN DETALLADA]
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=[piso]
    )

    conn.close()

    ubicaciones = (
        df['UBICACIÓN DETALLADA']
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return jsonify(ubicaciones)

@app.route('/guardar', methods=['POST'])
def guardar():

    data = request.json
    updates = data.get('updates', [])

    if not updates:
        return jsonify({
            'ok': False,
            'msg': 'No hay datos para guardar'
        }), 400

    conn = get_conn()
    cur = conn.cursor()

    try:

        for u in updates:

            rid = u.get('rid')
            piso = str(u.get('piso', '')).strip()
            ubicacion = str(u.get('ubicacion', '')).strip()

            if not piso or not ubicacion:

                conn.close()

                return jsonify({
                    'ok': False,
                    'msg': 'Debe completar todas las filas'
                }), 400

            cur.execute(
                """
                UPDATE base
                SET [PISO] = ?,
                    [UBICACIÓN DETALLADA] = ?
                WHERE rowid = ?
                """,
                (
                    piso,
                    ubicacion,
                    rid
                )
            )

        conn.commit()

    except Exception as e:

        conn.rollback()

        return jsonify({
            'ok': False,
            'msg': str(e)
        }), 500

    finally:

        conn.close()

    return jsonify({
        'ok': True,
        'msg': 'Datos guardados correctamente'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
