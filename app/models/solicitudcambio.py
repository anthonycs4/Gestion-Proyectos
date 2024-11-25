# app/models/solicitud_cambio.py

from datetime import datetime
from app import db

class SolicitudCambio(db.Model):
    __tablename__ = 'Solicitud_Cambio'
    
    id_cambio = db.Column(db.Integer, primary_key=True)
    id_proyecto = db.Column(db.Integer, db.ForeignKey('Proyecto.id_proyecto'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario'), nullable=False)
    archivo = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.Enum('Pendiente', 'Aprobado', 'Rechazado'), default='Pendiente')
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones con Proyecto y Usuario
    proyecto = db.relationship("Proyecto", back_populates="solicitudes_cambio")
    usuario = db.relationship("Usuario", back_populates="solicitudes_cambio")
