
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request, make_response, redirect, abort

app = Flask(__name__)

@app.route('/')
def hello_world():
    return """
    <h1>Hello World!</h1>
    <h2>Disciplina PTBDSWS</h2>
    """

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)

@app.route('/contextorequisicao')
def context():
    return f"""
    Your browser is {request.user_agent}
    """

@app.route("/codigostatusdiferente")
def status():
    return "Bad request", 400

@app.route("/objetoresposta")
def answer():
    response = make_response("<h1>This document carries a cookie!</h1>")
    response.set_cookie("answer", "true")
    return response

@app.route("/redirecionamento ")
def redirecting ():
    return redirect("https://ptb.ifsp.edu.br/")


@app.route("/abortar")
def abort_page():
    abort(404)