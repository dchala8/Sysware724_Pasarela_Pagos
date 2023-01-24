from ast import Not
import os
import re
import traceback
import json
import epaycosdk.epayco as epayco
from flask import request, jsonify, send_file
from datetime import datetime
from flask_cors import CORS, cross_origin
from flask_restful import Resource
#from src.modelos.modelos import User, db, Task
from werkzeug.utils import secure_filename
from src.utilities.utilities import allowed_file
from flask import current_app as app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
#from src.publisher import publish_task_queue
from sqlalchemy.sql import text

apiKey = "718dde0ecf0927abf30647f521a710c4"
privateKey = "db9f7a26a0e6da5a1769fe02354e5068"
lenguage = "ES"
test = False
options={"apiKey":apiKey,
         "privateKey":privateKey,
         "test":test,
         "lenguage":lenguage}


#APP STARTS HERE       
class Health(Resource):    
    @cross_origin()
    def get(self):
        return {"resultado": "OK", "mensaje": "service is alive"}, 200

    
class Client(Resource):    
    #Post Method - Creates a new Client
    @cross_origin()
    def post(self):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #create credit_card token
            credit_info = {
                "card[number]": request.json["cNumber"],
                "card[exp_year]": request.json["c_exp_year"],
                "card[exp_month]": request.json["c_exp_month"],
                "card[cvc]": request.json["c_cv"]
            }
            token=objepayco.token.create(credit_info)
            
            #create new client
            customer_info = {
                "token_card": token["id"],
                "name": request.json["client_name"],
                "last_name": request.json["client_lastname"], #This parameter is optional
                "email": request.json["client_email"],
                "phone": request.json["client_phone"],
                "default": True
            }
            customer=objepayco.customer.create(customer_info)
            
            #validar si el proceso por parte de epayco fue exitoso
            if customer["status"] == False:
                return {"resultado": "FALLO", "mensaje": "se presento un error al crear el cliente", "error": customer["message"] + " | " + customer["data"]["description"] + " | " + customer["data"]["errors"]}, 500
            
            #return a SUCCESS message and the newly created client
            return {"resultado": "OK", "mensaje": "cliente creado exitosamente", "cliente": customer}, 200
        
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al crear el cliente", "error": str(e)}, 500
        
    #Get Method - if client_id is 'all' it returns the list of all the clients, if client_id is a number it returns the client with that client_id
    @cross_origin()
    def get(self,client_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #Checks if it will return the whole list or just one client
            if client_id == 'all':
                #Uses Epayco platform to obtain all the associated clients
                customers = objepayco.customer.getlist()  
                
                if customers["status"] == False:
                    return {"resultado": "FALLO", "mensaje": "se presento un error al buscar el cliente", "error": customers["message"] + " | " + customers["data"]["description"]}, 500 
                              
                #return a SUCCESS message and the list of clients
                return {"resultado": "OK", "mensaje": "se obtuvo la lista de clientes exitosamente", "customers": customers}, 200
            else:
                #Uses Epayco platform to obtain just one asociated client using the client_id field
                customer=objepayco.customer.get(client_id)
                
                if customer["status"] == False:
                    return {"resultado": "FALLO", "mensaje": "se presento un error al buscar el cliente", "error": customer["message"] + " | " + customer["data"]["description"]}, 500 
                
                #return a SUCCESS message and the newly created client
                return {"resultado": "OK", "mensaje": "se obtuvo el cliente exitosamente", "cliente": customer}, 200
            
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al obtener los clientes", "error": str(e)}, 500


    #Put Method - receives a client_id and the name of the field to update in the url and a value for said field on the json body
    @cross_origin()
    def put(self,client_id):
        try:
            #Create API connection with EPAYCO
            objepayco=epayco.Epayco(options)
            
            #read dictionary with update fields and its values
            dicionaryString = request.json["dictionary"]
            dictionary = json.loads(dicionaryString)
            
            #field for the final response
            customer = None
            
            #Go trough the whole dictionary and updating the dictionary fields
            for key in dictionary:
                update_customer_info = {
                    key : dictionary[key]
                }
                customer = objepayco.customer.update(client_id,update_customer_info)
        
            #return a SUCCESS message and the newly updated client
            return {"resultado": "OK", "mensaje": "se actualizo el cliente exitosamente", "cliente": customer}, 200
        
        except Exception as e:
            return {"resultado": "FALLO", "mensaje": "se presento un error al actualizar el cliente", "error": str(e)}, 500        
    
