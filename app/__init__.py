# app/__init__.py
import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template
from flask_login import LoginManager
from app.controllers.MetodologiaController import metodologia  # Asegúrate de importar tu blueprint

from app.extensions import mysql, bcrypt, mail  # Importar las extensiones desde extensions.py
from app.controllers.UsuarioController import usuario_bp
from app.controllers.ProyectoController import proyecto_bp
from app.controllers.TareaController import tarea_bp
from app.controllers.InformeController import Informe
from app.controllers.MiembroController import miembro_bp  # Importa el blueprint



login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'esta_es_una_clave_secreta_muy_segura_1234'
    app.config['MYSQL_HOST'] = 'netdreams.pe'
    app.config['MYSQL_USER'] = 'netdrepe_anthony'
    app.config['MYSQL_PASSWORD'] = 'itIsnt4u'
    app.config['MYSQL_DB'] = 'netdrepe_gestion_de_proyectos'

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'ac2020067573@virtual.upt.pe'
    app.config['MAIL_PASSWORD'] = 'zkvs edsj vhmz xtza'

    # Inicializar extensiones
    mail.init_app(app)
    mysql.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'usuario.login'

    # Registrar blueprints
    app.register_blueprint(usuario_bp, url_prefix='/usuario')
    app.register_blueprint(proyecto_bp, url_prefix='/proyecto')
    app.register_blueprint(tarea_bp, url_prefix='/tarea')
    app.register_blueprint(Informe, url_prefix='/informe')
    app.register_blueprint(metodologia, url_prefix='/metodologia')  # Aquí registras el blueprint de metodologia
    app.register_blueprint(miembro_bp, url_prefix='/miembro')  # Prefijo opcional para las rutas del blueprint


    @app.route('/')
    def index():
        return render_template('index.html')

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.usuario import Usuario  # Importación diferida
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario, correo, nombre FROM Usuario WHERE id_usuario = %s", (user_id,))
    user_data = cur.fetchone()
    cur.close()
    if user_data:
        return Usuario(user_data[0], user_data[1], user_data[2])
    return None
