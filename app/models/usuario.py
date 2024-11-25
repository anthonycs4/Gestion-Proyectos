# app/models/usuario.py
from flask_login import UserMixin
from app.extensions import mysql, bcrypt

class Usuario(UserMixin):
    def __init__(self, id_usuario, correo, nombre, password=None, apellido=None, rol=None):
        self.id = id_usuario
        self.correo = correo
        self.nombre = nombre
        self.password = password
        self.apellido = apellido
        self.rol = rol  # Añadir rol al inicializar el usuario

    @classmethod
    def obtener_por_correo(cls, email):
        """Obtiene un usuario por su correo electrónico y busca su rol."""
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usuario, correo, password, nombre FROM Usuario WHERE correo = %s", (email,))
        user_data = cur.fetchone()
        
        if user_data:
            user = cls(id_usuario=user_data[0], correo=user_data[1], nombre=user_data[3], password=user_data[2])
            user.rol = user.obtener_rol()  # Obtener el rol del usuario desde miembro_proyecto
            return user
        return None

    def obtener_rol(self):
        """Obtiene el rol de mayor jerarquía del usuario desde la tabla miembro_proyecto."""
        cur = mysql.connection.cursor()
        cur.execute("""
              SELECT Rol.nombre FROM Miembro_Proyecto
        JOIN Rol ON Miembro_Proyecto.id_rol = Rol.id_rol
        WHERE Miembro_Proyecto.id_usuario = %s
        """, (self.id,))
        roles = cur.fetchall()
        print(roles)
        cur.close()
        
        # Convierte la lista de tuplas en una lista de strings
        roles = [rol[0] for rol in roles]
        
        # Define la jerarquía de roles
        if 'Administrador' in roles:
            print("admin")
            return 'Administrador'
        elif 'Líder de Proyecto' in roles:
            print("lider")
            return 'Líder de Proyecto'
        elif 'Desarrollador' in roles:
            print("desaroo")
            return 'Desarrollador'
        
        # En caso de que no se haya encontrado ningún rol
        return 'invitado'


    def verificar_password(self, password):
        """Verifica si la contraseña ingresada coincide con la almacenada."""
        if self.password:
            return bcrypt.check_password_hash(self.password, password)
        return False

    @staticmethod
    def registrar_usuario(nombre, apellido, correo, password):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Usuario WHERE correo = %s", (correo,))
        if cur.fetchone():
            cur.close()
            return False, 'El correo ya está registrado.'

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("""
            INSERT INTO Usuario (nombre, apellido, correo, password)
            VALUES (%s, %s, %s, %s)
        """, (nombre, apellido, correo, hashed_password))
        mysql.connection.commit()
        new_user_id = cur.lastrowid  # Obtener el ID del usuario recién creado
        cur.close()
        return True, new_user_id  # Devolver el ID en caso de éxito
