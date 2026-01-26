# Existing Codebase

## Schema

```sql
CREATE TABLE notifications_emailtemplate (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    body_text TEXT NOT NULL,
    body_html TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE notifications_emaillog (
    id BIGINT PRIMARY KEY,
    template_id BIGINT REFERENCES notifications_emailtemplate(id),
    recipient_email VARCHAR(254) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Models

```python
from django.db import models
from django.template import Context, Template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EmailTemplateManager(models.Manager):
    def get_by_name(self, name: str) -> Optional['EmailTemplate']:
        try:
            return self.get(name=name)
        except self.model.DoesNotExist:
            return None


class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=200)
    body_text = models.TextField()
    body_html = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = EmailTemplateManager()
    
    class Meta:
        db_table = 'notifications_emailtemplate'
    
    def __str__(self) -> str:
        return self.name
    
    def render_subject(self, context: Dict[str, Any]) -> str:
        template = Template(self.subject)
        return template.render(Context(context))
    
    def render_body_text(self, context: Dict[str, Any]) -> str:
        template = Template(self.body_text)
        return template.render(Context(context))
    
    def render_body_html(self, context: Dict[str, Any]) -> str:
        if not self.body_html:
            return ""
        template = Template(self.body_html)
        return template.render(Context(context))


class EmailLogStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SENT = 'sent', 'Sent'
    FAILED = 'failed', 'Failed'


class EmailLog(models.Model):
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=EmailLogStatus.choices,
        default=EmailLogStatus.PENDING
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications_emaillog'
    
    def __str__(self) -> str:
        return f"{self.template.name} to {self.recipient_email}"


class EmailService:
    @staticmethod
    def send_email(
        template_name: str,
        recipient_email: str,
        context: Dict[str, Any],
        from_email: Optional[str] = None
    ) -> EmailLog:
        template = EmailTemplate.objects.get_by_name(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        
        email_log = EmailLog.objects.create(
            template=template,
            recipient_email=recipient_email,
            subject=template.render_subject(context)
        )
        
        try:
            text_content = template.render_body_text(context)
            html_content = template.render_body_html(context)
            
            msg = EmailMultiAlternatives(
                subject=email_log.subject,
                body=text_content,
                from_email=from_email,
                to=[recipient_email]
            )
            
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            
            msg.send()
            
            email_log.status = EmailLogStatus.SENT
            email_log.sent_at = models.timezone.now()
            
        except Exception as e:
            email_log.status = EmailLogStatus.FAILED
            email_log.error_message = str(e)
            logger.error(f"Failed to send email: {e}")
        
        email_log.save()
        return email_log
```