# -*- coding: utf-8 -*-
from flask import Blueprint

api_blueprint = Blueprint('api', __name__,
                           template_folder='../../templates/api_1_0',
                           url_prefix='/api/v1.0')



