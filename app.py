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

    conn = get_conn()

    rows = conn.execute('SELECT * FROM base LIMIT 50').fetchall()

    conn.close()

    data = [dict(r) for r in rows]

    return jsonify(data)
