from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import User
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationService:
    """Servicio para enviar notificaciones a los usuarios"""
    
    def __init__(self, db: Session):
        """
        Inicializa el servicio con la sesión de base de datos
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
    
    async def send_service_request_notification(
        self, 
        user_id: int, 
        request_id: int, 
        service_name: str, 
        status: str
    ) -> bool:
        """
        Envía una notificación cuando cambia el estado de una solicitud de servicio
        
        Args:
            user_id: ID del usuario destinatario
            request_id: ID de la solicitud de servicio
            service_name: Nombre del servicio
            status: Nuevo estado de la solicitud
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        # Obtener el usuario
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.email:
            return False
        
        # Preparar el contenido según el estado
        subject = f"Actualización de tu solicitud de servicio: {service_name}"
        
        status_messages = {
            "pending": "Tu solicitud ha sido recibida y está pendiente de revisión.",
            "approved": "¡Buenas noticias! Tu solicitud ha sido aprobada y pronto comenzaremos a trabajar en ella.",
            "in_progress": "Hemos comenzado a trabajar en tu solicitud.",
            "completed": "¡Tu servicio ha sido completado! Revisa los resultados en tu panel.",
            "cancelled": "Tu solicitud ha sido cancelada."
        }
        
        message = f"""
        Hola {user.first_name},
        
        {status_messages.get(status, f'El estado de tu solicitud ha cambiado a: {status}')}
        
        Detalles de la solicitud:
        - Servicio: {service_name}
        - ID de solicitud: {request_id}
        - Estado actual: {status}
        
        Puedes ver más detalles iniciando sesión en tu cuenta y visitando la sección de solicitudes.
        
        Saludos,
        El equipo de SEO Analyzer
        """
        
        # Enviar el email
        return self._send_email(user.email, subject, message)
    
    async def send_new_service_request_admin_notification(
        self,
        service_name: str,
        user_email: str,
        request_id: int
    ) -> bool:
        """
        Notifica a los administradores sobre una nueva solicitud de servicio
        
        Args:
            service_name: Nombre del servicio solicitado
            user_email: Email del usuario que hizo la solicitud
            request_id: ID de la solicitud
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        # Obtener todos los usuarios administradores
        admin_users = self.db.query(User).filter(User.role == "admin").all()
        admin_emails = [user.email for user in admin_users if user.email]
        
        if not admin_emails:
            return False
        
        subject = f"Nueva solicitud de servicio: {service_name}"
        message = f"""
        Se ha recibido una nueva solicitud de servicio.
        
        Detalles:
        - Servicio: {service_name}
        - Usuario: {user_email}
        - ID de solicitud: {request_id}
        
        Por favor, revisa esta solicitud en el panel de administración lo antes posible.
        """
        
        # Enviar email a todos los administradores
        success = True
        for email in admin_emails:
            if not self._send_email(email, subject, message):
                success = False
        
        return success
    
    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Envía un email usando la configuración del sistema
        
        Args:
            recipient: Email del destinatario
            subject: Asunto del email
            body: Cuerpo del mensaje
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            # Crear mensaje
            message = MIMEMultipart()
            message["From"] = settings.FROM_EMAIL
            message["To"] = recipient
            message["Subject"] = subject
            
            # Adjuntar cuerpo del mensaje
            message.attach(MIMEText(body, "plain"))
            
            # Conectar y enviar
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                if settings.USE_TLS:
                    server.starttls()
                
                server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                server.send_message(message)
            
            return True
        
        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            return False