from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import psycopg2
import os
import tempfile

app = Flask(__name__)


# =========================
# CONEXIÓN POSTGRESQL
# =========================
def get_conn():

    return psycopg2.connect(
        os.environ.get("DATABASE_URL")
    )


# =========================
# HOME
# =========================
@app.route('/')
def index():
    return render_template('index.html')


# =========================
# BUSCAR DOCUMENTO
# =========================
@app.route('/buscar')
def buscar():

    doc = request.args.get('doc', '')

    conn = get_conn()

    query = '''
        SELECT *
        FROM base
        WHERE CAST("DOCUMENTO" AS TEXT) ILIKE %s
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


# =========================
# BUSCAR UBICACIONES
# =========================
@app.route('/ubicaciones')
def ubicaciones():

    piso = request.args.get('piso', '')

    conn = get_conn()

    query = '''
        SELECT *
        FROM base
        WHERE "PISO" ILIKE %s
        LIMIT 200
    '''

    df = pd.read_sql(
        query,
        conn,
        params=[f'%{piso}%']
    )

    conn.close()

    return jsonify(
        df.fillna('').to_dict(orient='records')
    )


# =========================
# GUARDAR CAMBIOS
# =========================
@app.route('/guardar', methods=['POST'])
def guardar():

    data = request.json

    updates = data.get('updates', [])

    conn = get_conn()

    cur = conn.cursor()

    for u in updates:

        rid = u.get('id') or u.get('rid')

        piso = u.get('piso') or u.get('PISO')

        ubicacion = (
            u.get('ubicacion')
            or u.get('UBICACIÓN DETALLADA')
        )

        cur.execute(
            '''
            UPDATE base
            SET "PISO"=%s,
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


# =========================
# EXPORTAR
# =========================
@app.route('/exportar')
def exportar():

    conn = get_conn()

    df = pd.read_sql(
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


# =========================
# VALIDAR
# =========================
@app.route('/validar')
def validar():

    conn = get_conn()

    df = pd.read_sql(
        'SELECT * FROM base LIMIT 50',
        conn
    )

    conn.close()

    return df.to_html(index=False)


# =========================
# MAIN
# =========================
if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 10000))
    )
