import os
import requests

#from datetime import datetime
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField

from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

class NameForm(FlaskForm):
  name = StringField('What is your name?', validators= [DataRequired()])
  role = SelectField('Role?:', choices=[ ('User', 'User'), ('Moderator', 'Moderator'), ('Admin', 'Administrator') ],  validators=[DataRequired()])
  send_confirmation = BooleanField()
  submit = SubmitField('Submit')

  #------------------->  forms agora tem: Input para nome; dropdown para Função e botão de Submit


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Chave forte'

# Mailgun config
# As informações são obtidas pelas variáveis de ambiente
app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['PERSONAL_EMAIL'] = os.environ.get('PERSONAL_EMAIL')
app.config['STUDENT_NAME'] = os.environ.get('STUDENT_NAME')
app.config['STUDENT_ID'] = os.environ.get('STUDENT_ID')

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return '<User %r>' % self.username


bootstrap = Bootstrap(app)
moment = Moment(app)

#-------------------------------> Função para enviar e-mail pelo Mailgun
def send_simple_message(username, role_name, send_confirmation):
    api_key = app.config['API_KEY']
    api_url = app.config['API_URL']
    sender = app.config['API_FROM']
    second_email = app.config['FLASKY_ADMIN']
    personal_email = app.config['PERSONAL_EMAIL']
    student_name = app.config['STUDENT_NAME']
    student_id = app.config['STUDENT_ID']

    # Verificação de configurações necessárias preenchidas
    if not all([
        api_key, api_url, sender,
        personal_email, student_name, student_id
    ]):
        app.logger.error('Mailgun configuration is incomplete.')
        return False

    subject = '[Flasky] Novo usuário cadastrado'

    text = (
        f'Um novo usuário foi cadastrado.\n\n'
        f'Nome do usuário: {username}\n'
        f'Função: {role_name}\n'
        f'Dados enviados a: {student_name}\n'
        f'{student_id}'
    )

    #Eu sempre recebo o e-mail
    recipients = [personal_email]

    # o outro recebe somente se o checkbox estiver marcado
    if send_confirmation:
        recipients.append(second_email)

    try:
        response = requests.post(
            api_url,
            auth=('api', api_key),
            data={
                'from': sender,
                'to': recipients,
                'subject': subject,
                'text': text
            },
            timeout=20
        )

        response.raise_for_status()
        app.logger.info('Mailgun accepted the email request.')
        return True

    except requests.RequestException:
        # Registra o erro sem expor a chave da API
        app.logger.exception('Mailgun email request failed.')
        return False




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
    form = NameForm()
    form.send_confirmation.label.text = f"Enviar e-mail para: {app.config['FLASKY_ADMIN']}"

    message = None
    message_type = None

    if form.validate_on_submit():
        username = form.name.data.strip()
        selected_role = form.role.data
        #------------------->  salva a opção escolhida no select

        existing_user = User.query.filter_by(username=username).first()
        #------------------->  função para verificar se o user já existe

        if existing_user is None: # cria usuário se constata que nao existe
            user_role = Role.query.filter_by(name=selected_role).first()
                                                #------------------->  procura função escolhida no db

            user = User(
                username=username,
                role=user_role
            )

            db.session.add(user)
            db.session.commit()

            #-------------------> Envia e-mail após cadastrar o novo usuário
            email_sent = send_simple_message(
                username,
                user_role.name,
                form.send_confirmation.data
                )
            form.name.data = ''

            if email_sent:
                message = f'Usuário "{username}" cadastrado com sucesso! E-mail enviado.'
                message_type = 'success'
            else:
                message = f'Usuário "{username}" cadastrado, mas o e-mail não foi enviado.'
                message_type = 'warning'

        else:
            message = f'O usuário "{username}" já está cadastrado!'
            message_type = 'warning'

    users = User.query.all()
    users_count = User.query.count()
    #-------------------> contagem de registros

    roles = Role.query.all()
    roles_count = Role.query.count()
    #-------------------> contagem da quantidade de funções

    return render_template(
        'formulario.html',
        form=form,
        users=users,
        users_count=users_count,
        roles=roles,
        roles_count=roles_count,
        message=message,
        message_type=message_type
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