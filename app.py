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

            # VALIDACION CAMPOS
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
                AND [Ubicación Detallada] = ?
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

            # GUARDAR
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
