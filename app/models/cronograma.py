# app/models/cronograma.py
from app import db

class Cronograma(db.Model):
    __tablename__ = 'Cronograma'
    
    id_cronograma = db.Column(db.Integer, primary_key=True)
    fechainicio = db.Column(db.Date)
    fechafin = db.Column(db.Date)
    
    # Clave foránea para proyecto
    id_proyecto = db.Column(db.Integer, db.ForeignKey('Proyecto.id_proyecto'))
    
    # Relación
    proyecto = db.relationship('Proyecto', back_populates='cronograma')
