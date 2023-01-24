import os
from pathlib import Path
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from src.servicios.servicios import Client, Health,   Bank
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)


api.add_resource(Health, '/health')
api.add_resource(Client, '/client/create')

jwt = JWTManager(app)