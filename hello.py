# A very simple Flask Hello World app for you to get started with...
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("home.html")



@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, {}!</h1>'.format(name)