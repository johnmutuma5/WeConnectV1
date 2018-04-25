from flask import Flask, jsonify, url_for

# Blueprints
from .v1 import v1
# from .v2 import v2

app = Flask (__name__)
app.config.from_object ('config.Config')

app.register_blueprint (v1, url_prefix = "/api/v1")
# app.register_blueprint (v2, url_prefix = "/api/v2")



@app.route('/', methods=['GET'])
def index():
    documentation = '<a href='\
        + url_for('v1.documentation', _external=True)\
        + '>documentation</a>'

    return '<h1>Welcome to WeConnect</h1>.\
            <br> Read %s for usage examples and sample data' %documentation
