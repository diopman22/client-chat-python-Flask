#!/usr/bin/python3
# -*- coding:utf-8 -*-
from flask import Flask

app = Flask(__name__)
app.secret_key = 'Pa$$w0rd123'
from app import views