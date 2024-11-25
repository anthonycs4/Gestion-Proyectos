from flask import Blueprint, render_template, request, redirect, session, url_for, flash, current_app
from flask_login import current_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.metodologia import Metodologia
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.extensions import mysql, bcrypt, mail  # Importar mail desde extensions.py

from flask_mail import Message
from random import randint


usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/')
def home():
    return render_template('index.html') 

@usuario_bp.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_proyecto, p.nombre, p.fechainicio, p.fechafin, p.descripcion, p.estado
        FROM Proyecto p
        JOIN Miembro_Proyecto mp ON p.id_proyecto = mp.id_proyecto
        WHERE mp.id_usuario = %s
    """, (current_user.id,))
    session['idusuario']=current_user.id
    proyectos = cur.fetchall()
    cur.close()
    return render_template('proyectos/proyectos.html', proyectos=proyectos)
# Ruta para registrar usuarios
@usuario_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']

        Usuario.registrar_usuario(nombre, email, password)
        
        flash('¡Cuenta creada con éxito! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('usuario.login'))  # Redirige al login después de registrar
    return render_template('index.html')

@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuario.obtener_por_correo(email)

        if user and user.verificar_password(password):
            # Generar código de verificación
            codigo_verificacion = randint(100000, 999999)
            session['codigo_verificacion'] = codigo_verificacion
            session['email_verificado'] = email  # Guardar email en la sesión temporalmente

            # Enviar código de verificación por correo
            enviar_codigo_verificacion(email, codigo_verificacion)

            flash('Código de verificación enviado a tu correo.', 'info')
            return redirect(url_for('usuario.verificar_codigo'))

        flash('Correo o contraseña incorrectos', 'danger')
    return render_template('index.html')

def enviar_codigo_verificacion(email, codigo):
    mensaje = Message(
        subject='Código de Verificación',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    mensaje.body = f'Tu código de verificación es: {codigo}'
    mail.send(mensaje)

@usuario_bp.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if request.method == 'POST':
        codigo_ingresado = request.form['codigo']

        # Verificar el código ingresado con el código en la sesión
        if 'codigo_verificacion' in session and codigo_ingresado == str(session['codigo_verificacion']):
            user = Usuario.obtener_por_correo(session['email_verificado'])
            login_user(user)  # Completar el inicio de sesión

            # Limpiar la sesión de códigos y emails temporales
            session.pop('codigo_verificacion', None)
            session.pop('email_verificado', None)

            # Almacenar el rol del usuario en la sesión
            session['role'] = user.rol
            print("rol:- ",user.rol)

            # Redirigir según el rol del usuario
            if user.rol == 'Administrador':
                return redirect(url_for('proyecto.dashboard', rol=session.get('role')))  # Cambia a la ruta correspondiente
            elif user.rol == 'Líder de Proyecto':
                return redirect(url_for('proyecto.dashboard', rol=session.get('role')))
            elif user.rol == 'Desarrollador':
                return redirect(url_for('proyecto.dashboard', rol=session.get('role')))

            flash('Has iniciado sesión con éxito.', 'success')
        else:
            flash('Código de verificación incorrecto.', 'danger')

    return render_template('verificar_codigo.html', rol=session.get('role'))  # Pasar rol al template



# Ruta principal del index
@usuario_bp.route('/index', methods=['GET'])
def index():
    return render_template('views/index.html')  # Ruta a tu vista de index

from app.models.proyecto import Proyecto  # Importa el modelo Proyecto si no está importado
@usuario_bp.route('/register_user', methods=['GET', 'POST'])
@login_required
def register_user():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form.get('apellido')
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']
        proyecto = request.form['proyecto']

        # Registrar el usuario y obtener el ID
        registrado, resultado = Usuario.registrar_usuario(nombre, apellido, email, password)
        if not registrado:
            flash(resultado, 'danger')
            return redirect(url_for('usuario.register_user'))

        new_user_id = resultado  # Ahora resultado contiene el ID del usuario recién registrado
        
        # Insertar en Miembro_Proyecto
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Miembro_Proyecto (id_usuario, id_rol, id_proyecto)
            VALUES (%s, %s, %s)
        """, (new_user_id, rol, proyecto))
        mysql.connection.commit()
        cur.close()

        flash('¡Usuario registrado con éxito!', 'success')
        return redirect(url_for('usuario.dashboard'))

    # Obtener roles
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_rol, nombre FROM Rol")
    roles = cur.fetchall()

    # Obtener proyectos del usuario
    proyectos = Proyecto.obtener_proyectos_usuario(current_user.id)
    proyectos_nombres = [(p.id_proyecto, p.nombre) for p in proyectos]

    cur.close()

    return render_template('Mantenimiento/register_user.html', roles=roles, proyectos=proyectos_nombres)
