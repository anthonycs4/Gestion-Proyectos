# app/models/miembro_proyecto.py
from app.extensions import mysql

class MiembroProyecto:
    @staticmethod
    def obtener_usuarios_con_proyectos():
        """Obtener todos los usuarios con proyectos asignados y su rol"""
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.id_usuario, u.nombre, u.apellido, u.correo, 
                   p.nombre AS nombre_proyecto, 
                   r.nombre AS nombre_rol, 
                   mp.estado AS estado_miembro
            FROM Usuario u
            JOIN Miembro_Proyecto mp ON u.id_usuario = mp.id_usuario
            JOIN Proyecto p ON mp.id_proyecto = p.id_proyecto
            JOIN Rol r ON mp.id_rol = r.id_rol
            
        """)
        usuarios_con_proyectos = cur.fetchall()
        cur.close()
        return usuarios_con_proyectos

    @staticmethod
    def actualizar_rol(id_usuario, nuevo_rol_id):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE Miembro_Proyecto SET id_rol = %s WHERE id_usuario = %s", (nuevo_rol_id, id_usuario))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def cambiar_estado(id_usuario):
        cur = mysql.connection.cursor()
        cur.execute("SELECT estado FROM Miembro_Proyecto WHERE id_usuario = %s", (id_usuario,))
        estado_actual = cur.fetchone()[0]
        print(f"Estado actual: {estado_actual}")  # Verificar el estado actual
        
        # Alternar estado
        nuevo_estado = 'Eliminado' if estado_actual == 'Activo' else 'Activo'
        print(f"Nuevo estado: {nuevo_estado}")  # Verificar el nuevo estado
        
        # Intentar actualizar el estado
        cur.execute("UPDATE Miembro_Proyecto SET estado = %s WHERE id_usuario = %s", (nuevo_estado, id_usuario))
        mysql.connection.commit()
        
        # Verificar si la consulta afectó alguna fila
        print(f"Filas afectadas por el UPDATE: {cur.rowcount}")  # Esto debería ser 1 si la actualización tuvo éxito
        
        cur.close()


    @staticmethod
    def asignar_proyecto(id_usuario, id_proyecto, id_rol):
        """Asigna un proyecto y rol a un usuario"""
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Miembro_Proyecto (id_usuario, id_proyecto, id_rol, estado) 
            VALUES (%s, %s, %s, 'Activo')
        """, (id_usuario, id_proyecto, id_rol))
        mysql.connection.commit()
        cur.close()

    
    @staticmethod
    def obtener_roles():
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_rol, nombre FROM Rol")
        roles = cur.fetchall()
        cur.close()
        return roles

    @staticmethod
    def obtener_proyectos(id_usuario):
        cur = mysql.connection.cursor()
        # Modificamos la consulta para que solo devuelva proyectos donde el usuario no esté asignado
        cur.execute("""
            SELECT p.id_proyecto, p.nombre 
            FROM Proyecto p 
            WHERE p.estado = 'Activo' 
            AND p.id_proyecto NOT IN (
                SELECT mp.id_proyecto 
                FROM Miembro_Proyecto mp 
                WHERE mp.id_usuario = %s
            )
        """, (id_usuario,))
        proyectos = cur.fetchall()
        print(proyectos)  # Verificación
        cur.close()
        return proyectos
