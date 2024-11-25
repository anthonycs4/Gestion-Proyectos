# app/models/informe_estado.py
from datetime import datetime
from app import db

class InformeEstado(db.Model):
    __tablename__ = 'Informe_Estado'
    
    id_informe = db.Column(db.Integer, primary_key=True)
    id_proyecto = db.Column(db.Integer, db.ForeignKey('Proyecto.id_proyecto'), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    avance_general = db.Column(db.Text, nullable=True)
    problemas = db.Column(db.Text, nullable=True)

    # Relación con Proyecto
    proyecto = db.relationship("Proyecto", back_populates="informes_estado")
