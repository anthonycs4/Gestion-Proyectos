# app/models/informe_cambio.py
from app import db

class InformeCambio(db.Model):
    __tablename__ = 'Informe_Cambio'
    
    id_informe_cambio = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50))
    tiempo = db.Column(db.Float)
    costo = db.Column(db.Float)
    estado = db.Column(db.String(50))
    
    # Clave foránea
    id_solicitud_cambio = db.Column(db.Integer, db.ForeignKey('Solicitud_Cambio.id_cambio'))
    
    # Relación
    solicitud_cambio = db.relationship('SolicitudCambio')
