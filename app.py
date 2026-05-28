from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
import tempfile
app=Flask(__name__)
DB='database.db'
def c():
    x=sqlite3.connect(DB)
    x.row_factory=sqlite3.Row
    return x
@app.route('/')
def i():
    return render_template('index.html')
@app.route('/buscar')
def b():
    doc=request.args.get('doc','')
    x=c()
    rows=[dict(r) for r in x.execute('SELECT rowid rid,* FROM base WHERE [Doc. Identidad] = ?', (doc,)).fetchall()]
    pisos=[r[0] for r in x.execute('SELECT DISTINCT [Piso] FROM nomenclatura ORDER BY [Piso]').fetchall()]
    x.close()
    return jsonify({'rows':rows,'pisos':pisos})
@app.route('/ubicaciones')
def u():
    piso=request.args.get('piso','')
    x=c()
    data=[r[0] for r in x.execute('SELECT DISTINCT [Ubicación Detallada] FROM nomenclatura WHERE [Piso] = ? ORDER BY [Ubicación Detallada]',(piso,)).fetchall()]
    x.close()
    return jsonify(data)
@app.route('/guardar', methods=['POST'])
def g():

    data = request.get_json()

    ups = data.get('updates', [])

    if not ups:

        return jsonify({
            'ok': False,
            'msg': 'No hay datos para guardar'
        }), 400

    x = c()

    try:

        for u in ups:

            piso = str(u.get('piso', '')).strip()
            ubicacion = str(u.get('ubicacion', '')).strip()
            rid = u.get('rid')

            # VALIDACION
            if not piso or not ubicacion:

                x.close()

                return jsonify({
                    'ok': False,
                    'msg': 'Debe completar todas las filas'
                }), 400

            # VALIDAR PISO + UBICACION
            existe = x.execute(
                '''
                SELECT 1
                FROM nomenclatura
                WHERE [Piso] = ?
                AND [UBICACIÓN DETALLADA] = ?
                LIMIT 1
                ''',
                (piso, ubicacion)
            ).fetchone()

            if not existe:

                x.close()

                return jsonify({
                    'ok': False,
                    'msg': 'La ubicación no corresponde al piso'
                }), 400

            # UPDATE REAL
            x.execute(
                '''
                UPDATE base
                SET
                    [Piso] = ?,
                    [Ubicación Detallada] = ?
                WHERE rowid = ?
                ''',
                (
                    piso,
                    ubicacion,
                    rid
                )
            )

        x.commit()

    except Exception as e:

        x.rollback()

        return jsonify({
            'ok': False,
            'msg': str(e)
        }), 500

    finally:

        x.close()

    return jsonify({
        'ok': True,
        'msg': 'Datos guardados correctamente'
    })
@app.route('/validar')
def validar():

    x = c()

    rows = x.execute(
        'SELECT * FROM base'
    ).fetchall()

    x.close()

    html = '''
    <html>
    <head>

        <title>Validación</title>

        <style>

        body{
            font-family:Arial;
            margin:20px;
        }

        table{
            border-collapse:collapse;
            width:100%;
        }

        th,td{
            border:1px solid #ccc;
            padding:8px;
            font-size:12px;
        }

        th{
            background:#f0f0f0;
            position:sticky;
            top:0;
        }

        button{
            padding:10px;
            cursor:pointer;
        }

        </style>

    </head>

    <body>

    <h2>Datos almacenados</h2>

    <a href="/excel">
        <button>Descargar Excel</button>
    </a>

    <br><br>

    <table>
    '''

    if rows:

        cols = rows[0].keys()

        html += '<tr>'

        for c1 in cols:
            html += f'<th>{c1}</th>'

        html += '</tr>'

        for r in rows:

            html += '<tr>'

            for c1 in cols:
                html += f'<td>{r[c1]}</td>'

            html += '</tr>'

    html += '''
    </table>

    </body>
    </html>
    '''

    return html
