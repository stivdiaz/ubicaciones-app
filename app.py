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
