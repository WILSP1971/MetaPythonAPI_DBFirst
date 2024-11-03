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
import http.client
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
    mensajelog = db.Column(db.TEXT)

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
    nuevo_registro = Log(mensajelog=texto)
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
    challenge = req.args.get('hub.challenge')

    #and challenge
    if token == TOKEN_TWSCODE:
        return challenge
    else:
        return jsonify({'error':'TOKEN INVAVALIDO'}),401


def recibir_mensajes(req):
    # req = request.get_json()
    # agregar_mensajes_log(req)
    
    try:
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']
        
        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages["type"]
                if tipo == "interactive":
                    return 0
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]
                    agregar_mensajes_log(json.dumps(text))
                    agregar_mensajes_log(json.dumps(numero))

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'error':'ERROR'})

def enviar_mensaje_whatapps(texto,number):
    texto = texto.lower()
    if "hola" in texto:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, ¿Cómo estás? Bienvenido."
            }
        }
    else:
        data={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hola, visita mi web twsbarranquilla.com para más información.\n \n📌Por favor, ingresa un número #️⃣ para recibir información.\n \n1️⃣. Información del Curso. ❔\n2️⃣. Ubicación del local. 📍\n3️⃣. Enviar temario en PDF. 📄\n4️⃣. Audio explicando curso. 🎧\n5️⃣. Video de Introducción. ⏯️\n6️⃣. Hablar con AnderCode. 🙋‍♂️\n7️⃣. Horario de Atención. 🕜 \n0️⃣. Regresar al Menú. 🕜"
            }
        }

    ## Convertir a el diccionario en formato json
    data = json.dumps(data)        

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAAPgwBHqKVgBO18PVpQ9BWTsRWH7o1pr9Mc4xMFsl7CkvaXwiGZAkwSkHHjWRAtaZAidiZB6dx4ZAqY2v57mwjECfkqUsFlCn1ZCQe4pF02keC3ljS3mpo8P5KLvrXjPxvHh10wDlMTbvACx2ejZC5U1aqOb2n5KopjV71rrwgGGG09tVEnOKLmEHoZBb3ZArzcTvGhR2ik06RiM04Ci5ZAv9GzIZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v21.0/489807960875135/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)





    
