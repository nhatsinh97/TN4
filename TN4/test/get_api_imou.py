import ast
import json
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/api', methods = ['POST'])
def api_imou():
    data = ast.literal_eval(request.data.decode())
    return data

app.run(host='0.0.0.0', port=5000 ,debug=True)