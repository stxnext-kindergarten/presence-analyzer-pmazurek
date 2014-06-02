# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
from flask import Flask
from flask.ext.mako import MakoTemplates  # pylint: disable-msg=E0611

app = Flask(__name__)  # pylint: disable=C0103
mako = MakoTemplates(app)
