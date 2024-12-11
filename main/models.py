from bson import ObjectId
from django.db import models
from djongo.models import ObjectIdField


from django.db import models
from djongo.models import ObjectIdField

class User(models.Model):
    _id = ObjectIdField(primary_key=True)  # Use MongoDB's _id as Django's primary key
    username = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    alternate_phone_number = models.CharField(max_length=15, blank=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    # Fields specific to clients
    full_name = models.CharField(max_length=255, blank=True, null=True)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Validate that client-specific fields are provided when not admin
        if not self.is_admin:
            if not self.full_name:
                raise ValueError("Full name is required for clients.")
            if not self.national_id:
                raise ValueError("National ID is required for clients.")
            if not self.address:
                raise ValueError("Address is required for clients.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Request(models.Model):
    id = models.CharField(
        primary_key=True, default=lambda: str(ObjectId()), editable=False, max_length=24
    )
    REQUEST_TYPES = [
        ('new', 'New Request'),
        ('complaint', 'Complaint'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_processing', 'Under Processing'),
        ('closed', 'Closed'),
    ]

    admin_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='admin_requests'
    )
    client_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_requests'
    )
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    request_date = models.DateTimeField(auto_now_add=True)
    last_update_date = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Request {self.id} ({self.get_request_type_display()})"


class Attachment(models.Model):
    id = models.CharField(
        primary_key=True, default=lambda: str(ObjectId()), editable=False, max_length=24
    )
    request = models.ForeignKey(
        'Request',
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment {self.id} for Request {self.request.id}"
