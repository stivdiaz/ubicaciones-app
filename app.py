from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
import tempfile

app = Flask(__name__)

DB = 'database.db'


def c():
    x = sqlite3.connect(DB)
    x.row_factory = sqlite3.Row
    return x


@app.route('/')
def i():
    return render_template('index.html')

# BUSCAR POR DOCUMENTO
@app.route('/buscar')
def b():

    doc = request.args.get('doc', '').strip()

    x = c()

    rows = [
        dict(r) for r in x.execute(
            '''
            SELECT
                rowid as rid,
                *
            FROM base
            WHERE [Doc. Identidad] = ?
            ''',
            (doc,)
        ).fetchall()
    ]

    pisos = [
        r[0] for r in x.execute(
            '''
            SELECT DISTINCT [Piso]
            FROM nomenclatura
            WHERE [Piso] IS NOT NULL
            ORDER BY [Piso]
            '''
        ).fetchall()
    ]

    x.close()

    return jsonify({
        'rows': rows,
        'pisos': pisos
    })


# UBICACIONES DEPENDIENTES DEL PISO
@app.route('/ubicaciones')
def u():

    piso = request.args.get('piso', '').strip()

    x = c()

    data = [
        r[0] for r in x.execute(
            '''
            SELECT DISTINCT [Ubicación Detallada]
            FROM nomenclatura
            WHERE [Piso] = ?
            ORDER BY [Ubicación Detallada]
            ''',
            (piso,)
        ).fetchall()
    ]

    x.close()

    return jsonify(data)


# GUARDAR
@app.route('/guardar', methods=['POST'])
def g():

    data = request.get_json()

    updates = data.get('updates', [])

    if not updates:
        return jsonify({
            'ok': False,
            'msg': 'No hay datos para guardar'
        }), 400

    x = c()

    for u in updates:

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

        # VALIDAR UBICACION VS PISO
        validacion = x.execute(
            '''
            SELECT 1
            FROM nomenclatura
            WHERE [Piso] = ?
            AND [Ubicación Detallada] = ?
            LIMIT 1
            ''',
            (piso, ubicacion)
        ).fetchone()

        if not validacion:

            x.close()

            return jsonify({
                'ok': False,
                'msg': 'La ubicación no corresponde al piso'
            }), 400

        # GUARDAR
        x.execute(
            '''
            UPDATE base
            SET
                [Piso] = ?,
                [Ubicación Detallada] = ?
            WHERE rowid = ?
            ''',
            (piso, ubicacion, rid)
        )

    x.commit()
    x.close()

    return jsonify({
        'ok': True,
        'msg': 'Datos guardados correctamente'
    })


# VALIDAR DATOS
@app.route('/validar')
def validar():

    x = c()

    rows = [
        dict(r) for r in x.execute(
            'SELECT * FROM base LIMIT 50'
        ).fetchall()
    ]

    x.close()

    return jsonify(rows)
