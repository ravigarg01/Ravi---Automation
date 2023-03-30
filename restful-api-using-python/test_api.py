# from flask import Flask,render_template, request
# import flask_pymssql
# from flask_pymssql import PyMSSQL
# import json

# app = Flask(name)

# app.config['MSSQL_HOST'] = 'localhost'
# app.config['MSSQL_USER'] = 'root'
# app.config['MSSQL_PASSWORD'] = 'R@vig@rg1907'
# app.config['MSSQL_DB'] = 'asins'
 
# mssql = PyMSSQL(app)
 
# @app.route('/asins', methods = ['GET'])
# def asins():
#     if request.method == 'GET':
#         cursor = mssql.connection.cursor()
#         cursor.execute(''' SELECT asin FROM asin_status''')
#         data = cursor.fetchall()
#         cursor.close()
#         return json.dumps(data)
        
    
# app.run(host='localhost', port=5000)


from flask import Flask,render_template, request
import pyodbc
import json
import waitress

app = Flask(__name__)

connect = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
'Server=Ravi-Digital-PC\SQLEXPRESS;'
'Database=amazon;''Trusted_Connection=yes;')

@app.route('/asins', methods = ['GET'])
def asins():
    if request.method == 'GET':
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM asin_status WHERE status = ?", ("Active & Starred"))
        rows = cursor.fetchall()
        data = [
            {'asin': row[0], 
            'status': row[1], 
            'book_code': row[2],
            'company': row[3],
            'book_name': row[4],
            'price': row[5],
            'ecom_title' : row[6],
            'node' : row[7],
            'book_type' : row[8],
            'book_pages' : row[9],
            'adc_weight' : row[10]} 
            for row in rows]
        cursor.close()
        return json.dumps(data)
      

# app.run(host='0.0.0.0', port=5000)
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)