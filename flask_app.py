from datetime import datetime
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
  name = StringField('What is your name?', validators= [DataRequired()])
  submit = SubmitField('Submit')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Chave forte'
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#@app.route("/")
#def home():

#    return render_template(
#        "home.html",
#        current_time=datetime.now()
#    )

@app.route('/', methods=['GET', 'POST'])
def home():
  name = None
  form = NameForm()
  if form.validate_on_submit():
    name = form.name.data
    form.name.data = ''
  return render_template('formulario.html',
                         form=form,
                         name=name
    )



@app.route('/user/<name>/<pront>/<insti>')
def user(name, pront, insti):
    return render_template(
        "user.html",
        name=name,
        pront=pront,
        insti=insti
    )

@app.route('/contextorequisicao/<name>')
def contextorequisicao(name):
     return render_template(
        "contextorequisicao.html",
        name=name,
        browser=request.headers.get('User-Agent'),
        ip=request.remote_addr,
        host=request.host
    )

#@app.route("/codigostatusdiferente")
#def status():
#    return "Bad request", 400

#@app.route("/objetoresposta")
#def answer():
#    response = make_response("<h1>This document carries a cookie!</h1>")
#    response.set_cookie("answer", "true")
#    return response

#@app.route("/redirecionamento ")
#def redirecting ():
#    return redirect("https://ptb.ifsp.edu.br/")


#@app.route("/abortar")
#def abort_page():
#    abort(404)