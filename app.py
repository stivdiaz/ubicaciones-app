from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB = 'database.db'

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar')
def buscar():
    doc = request.args.get('doc')
    conn = get_conn()
    
    # Selecciona rowid como rid y las columnas solicitadas
    q = 'SELECT rowid as rid, * FROM base WHERE [Doc. Identidad]=?'
    rows = [dict(r) for r in conn.execute(q, (doc,)).fetchall()]
    
    # Obtiene pisos únicos sin duplicados
    pisos = [r[0] for r in conn.execute('SELECT DISTINCT Piso FROM nomenclatura WHERE Piso IS NOT NULL ORDER BY Piso').fetchall()]
    conn.close()
    
    return jsonify({'rows': rows, 'pisos': pisos})

@app.route('/ubicaciones')
def ubicaciones():
    piso = request.args.get('piso')
    conn = get_conn()
    data = [r[0] for r in conn.execute('SELECT DISTINCT [Ubicación Detallada] FROM nomenclatura WHERE Piso=? ORDER BY [Ubicación Detallada]', (piso,)).fetchall()]
    conn.close()
    return jsonify(data)

@app.route('/guardar', methods=['POST'])
def guardar():
    data = request.json
    updates = data.get('updates', [])

    # Validación backend obligatoria
    for u in updates:
        if not u.get('piso') or not u.get('ubicacion'):
            return jsonify({
                'ok': False,
                'msg': 'Debe completar todas las filas'
            }), 400

    conn = get_conn()
    cur = conn.cursor()

    try:
        for u in updates:
            # Corregido a '?' para SQLite y usando rowid (rid)
            cur.execute(
                '''
                UPDATE base
                SET [PISO] = ?,
                    [UBICACIÓN DETALLADA] = ?
                WHERE rowid = ?
                ''',
                (u['piso'], u['ubicacion'], u['rid'])
            )
        conn.commit()
        msg = 'Datos guardados correctamente'
        ok = True
    except Exception as e:
        conn.rollback()
        msg = f'Error al guardar en la base de datos: {str(e)}'
        ok = False
    finally:
        cur.close()
        conn.close()

    return jsonify({'ok': ok, 'msg': msg})

@app.route('/validar')
def validar():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT rowid, * FROM base")
    rows = cur.fetchall()
    columnas = [desc[0] for desc in cur.description]

    html = "<h1>Datos almacenados (Vista de Validación)</h1>"
    html += '<table border="1" cellpadding="5" style="border-collapse:collapse;"><tr>'
    for col in columnas:
        html += f"<th>{col}</th>"
    html += "</tr>"

    for row in rows:
        html += "<tr>"
        for val in row:
            html += f"<td>{val if val is not None else ''}</td>"
        html += "</tr>"

    html += "</table>"
    cur.close()
    conn.close()
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
