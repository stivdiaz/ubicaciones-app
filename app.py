
from flask import Flask, render_template, request, jsonify
import pandas as pd
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar')
def buscar():

    doc = request.args.get('doc', '')

    conn = get_conn()

    query = '''
        SELECT *
        FROM base
        WHERE CAST("Doc. Identidad" AS TEXT) ILIKE %s
        LIMIT 50
    '''

    df = pd.read_sql(
        query,
        conn,
        params=[f'%{doc}%']
    )

    conn.close()

    return jsonify(
        df.fillna('').to_dict(orient='records')
    )

@app.route('/ubicaciones')
def ubicaciones():

    piso = request.args.get('piso', '')

    conn = get_conn()

    query = '''
        SELECT DISTINCT "UBICACIÓN DETALLADA"
        FROM base
        WHERE piso = %s
        ORDER BY "UBICACIÓN DETALLADA"
    '''

    df = pd.read_sql(
        query,
        conn,
        params=[piso]
    )

    conn.close()

    return jsonify(
        df['UBICACIÓN DETALLADA'].dropna().unique().tolist()
    )

@app.route('/pisos')
def pisos():

    conn = get_conn()

    query = '''
        SELECT DISTINCT piso
        FROM base
        WHERE piso IS NOT NULL
        ORDER BY piso
    '''

    df = pd.read_sql(query, conn)

    conn.close()

    return jsonify(
        df['piso'].dropna().unique().tolist()
    )

@app.route('/guardar', methods=['POST'])
def guardar():

    data = request.json
    updates = data.get('updates', [])

    conn = get_conn()
    cur = conn.cursor()

    for u in updates:

        rid = u.get('id')

        piso = u.get('piso')
        ubicacion = u.get('ubicacion')

        if not piso or not ubicacion:
            return jsonify({
                'ok': False,
                'msg': 'Debe completar todas las filas'
            }), 400

        cur.execute(
            '''
            UPDATE base
            SET piso=%s,
                "UBICACIÓN DETALLADA"=%s
            WHERE id=%s
            ''',
            (
                piso,
                ubicacion,
                rid
            )
        )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        'ok': True,
        'msg': 'Datos guardados correctamente'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
