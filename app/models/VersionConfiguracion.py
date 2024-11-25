# app/models/version_configuracion.py
from app import db

class VersionConfiguracion(db.Model):
    __tablename__ = 'Version_Configuracion'
    
    id_version = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum('Documento', 'Código'), nullable=False)
    fecha_subida = db.Column(db.Date, nullable=False)

    # Relación con Proyecto
    id_proyecto = db.Column(db.Integer, db.ForeignKey('Proyecto.id_proyecto'), nullable=False)
    proyecto = db.relationship('Proyecto', back_populates='version_configuracion')

    def __repr__(self):
        return f"<VersionConfiguracion {self.id_version} - {self.version}>"
