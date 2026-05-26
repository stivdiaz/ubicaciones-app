from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB='database.db'

def get_conn():
    conn=sqlite3.connect(DB)
    conn.row_factory=sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar')
def buscar():
    doc=request.args.get('doc')
    conn=get_conn()
    q='SELECT rowid as rid, * FROM base WHERE [Doc. Identidad]=?'
    rows=[dict(r) for r in conn.execute(q,(doc,)).fetchall()]
    pisos=[r[0] for r in conn.execute('SELECT DISTINCT Piso FROM nomenclatura WHERE Piso IS NOT NULL ORDER BY Piso').fetchall()]
    conn.close()
    return jsonify({'rows':rows,'pisos':pisos})

@app.route('/ubicaciones')
def ubicaciones():
    piso=request.args.get('piso')
    conn=get_conn()
    data=[r[0] for r in conn.execute('SELECT DISTINCT [Ubicación Detallada] FROM nomenclatura WHERE Piso=? ORDER BY [Ubicación Detallada]',(piso,)).fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/guardar', methods=['POST'])
def guardar():

    data = request.json

    updates = data.get('updates', [])

    for u in updates:

        if not u.get('piso') or not u.get('ubicacion'):

            return jsonify({
                'ok': False,
                'msg': 'Debe completar todas las filas'
            }), 400

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

@app.route('/validar')
def validar():

    conn = get_conn()

    cur = conn.cursor()

    cur.execute("SELECT * FROM base")

    rows = cur.fetchall()

    columnas = [desc[0] for desc in cur.description]

    html = """
    <h1>Datos almacenados</h1>
    <table border="1" cellpadding="5">
    <tr>
    """

    for col in columnas:
        html += f"<th>{col}</th>"

    html += "</tr>"

    for row in rows:

        html += "<tr>"

        for val in row:
            html += f"<td>{val}</td>"

        html += "</tr>"

    html += "</table>"

    cur.close()
    conn.close()

    return html
    return str(rows)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)

