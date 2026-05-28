from flask import Flask, render_template, request, jsonify
import sqlite3
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
    data=request.get_json()
    ups=data.get('updates',[])
    x=c()
    for u in ups:
        x.execute('UPDATE base SET [PISO] = ?, [UBICACIÓN DETALLADA] = ? WHERE rowid = ?',(u['piso'],u['ubicacion'],u['rid']))
    x.commit();x.close()
    return jsonify({'msg':'Datos guardados correctamente'})

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

        .btn{
            background:#1976d2;
            color:white;
            border:none;
            padding:10px 15px;
            cursor:pointer;
            border-radius:5px;
            margin-bottom:15px;
        }

        </style>

    </head>

    <body>

    <h2>Datos almacenados</h2>

    <a href="/excel">
        <button class="btn">
            Descargar Excel
        </button>
    </a>

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
