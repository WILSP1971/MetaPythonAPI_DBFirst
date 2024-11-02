#### EJEMPLO 1 - PAGINA HTML
####
# from flask import Flask,render_template
# app = Flask(__name__)
# @app.route('/')
# def hola_mundo():
#     return render_template('holaflask.html')

# if __name__ == '__main__':
#     app.run(debug=True)
#     ## Subir a Render
#     ## app.run(host='0.0.0.0',port='8082',debug=True)

#### EJEMPLO 2 - BASES DE DATOS
####

import datetime
import json
from flask import Flask,render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

## Configuracion BD SQLLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

## Definicion de tablas con sus columnas
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fechahora = db.Column(db.DateTime, default=datetime.datetime.today)
    Observacion = db.Column(db.TEXT)

## Creacion tabla si no existe
with app.app_context():
    db.create_all()

    # mensaje1 = Log(Observacion = "Mensaje 1")
    # mensaje2 = Log(Observacion = "Mensaje 2")

    # db.session.add(mensaje1)
    # db.session.add(mensaje2)
    # db.session.commit()

## Ordenacion de registros por fecha, hora
def ordenar_fechahora(registros):
    return sorted(registros, key=lambda x:x.fechahora, reverse=True)

@app.route('/')

## Obtener registros de la tabla
def index():
    registros = Log.query.all()
    registros_ordenados = ordenar_fechahora(registros)
    return render_template('index.html',registros=registros_ordenados)

## Funcion de Guardar en BD Array de mensajes
mensajes_log = []

def agregar_mensajes_log(texto):
    mensajes_log.append(texto)
    #Guardar el mensaje en BD
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()


## TOKEN de Verificacion para la configuracion
TOKEN_TWSCODE = "TWSCODE"

## Creacion de WwbHook
@app.route('/webhook',methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.chellenge')

    if token and challenge == TOKEN_TWSCODE:
        return challenge
    else:
        return jsonify({'error':'TOKEN INVAVALIDO'}),401


def recibir_mensajes(req):
    req = request.get_json()
    agregar_mensajes_log()
    
    return jsonify({'message':'EVENT_RECEIVED'})


    
## Ejecucion de mensajes
#agregar_mensajes_log(json.dumps("Test1"))




if __name__ == '__main__':
    app.run(debug=True)





    