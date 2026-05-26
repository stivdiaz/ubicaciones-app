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
    return psycopg2.connect(os.environ.get("DATABASE_URL"))


# =========================
# INICIO
# =========================
@app.route('/')
def index():
    return render_template('index.html')


# =========================
# CONSULTAR DATOS
# =========================
@app.route('/consultar', methods=['POST'])
def consultar():

    data = request.json

    piso = data.get('piso', '')
    ubicacion = data.get('ubicacion', '')

    conn = get_conn()

    query = '''
        SELECT
            id,
            "PISO",
            "UBICACIÓN DETALLADA"
        FROM base
        WHERE 1=1
    '''

    params = []

    if piso:
        query += ' AND "PISO" ILIKE %s'
        params.append(f'%{piso}%')

    if ubicacion:
        query += ' AND "UBICACIÓN DETALLADA" ILIKE %s'
        params.append(f'%{ubicacion}%')

    query += ' LIMIT 200'

    df = pd.read_sql(query, conn, params=params)

    conn.close()

    resultados = []

    for _, row in df.iterrows():

        resultados.append({
            'rid': row['id'],
            'piso': row['PISO'],
            'ubicacion': row['UBICACIÓN DETALLADA']
        })

    return jsonify(resultados)

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

        cur.execute(
            '''
            UPDATE base
            SET "PISO"=%s,
                "UBICACIÓN DETALLADA"=%s
            WHERE id=%s
            ''',
            (
                u['piso'],
                u['ubicacion'],
                u['rid']
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
# EXPORTAR EXCEL
# =========================
@app.route('/exportar')
def exportar():

    conn = get_conn()

    df = pd.read_sql('SELECT * FROM base', conn)

    conn.close()

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix='.xlsx'
    )

    with pd.ExcelWriter(temp.name, engine='openpyxl') as writer:
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
# VALIDAR DATOS
# =========================
@app.route('/validar')
def validar():

    conn = get_conn()

    df = pd.read_sql(
        '''
        SELECT id,
               "PISO",
               "UBICACIÓN DETALLADA"
        FROM base
        LIMIT 20
        ''',
        conn
    )

    conn.close()

    return df.to_html(index=False)


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    app.run(debug=True)
