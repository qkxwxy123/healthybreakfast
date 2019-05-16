from flask import Flask , request
import logging
import logging.config
import pymysql

app = Flask(__name__)
db = pymysql.connect('localhost' , 'root' , 'qkx123' , 'healthybreakfast' , charset = 'utf8')
