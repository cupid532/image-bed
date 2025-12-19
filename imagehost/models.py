import os
import hashlib
import uuid
from datetime import datetime
from django.db import models
from django.conf import settings
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def generate_filename(instance, filename):
    """Generate unique filename based on hash and timestamp"""
    ext = os.path.splitext(filename)[1].lower()
    timestamp = datetime.now().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}/{unique_id}{ext}"


class Image(models.Model):
    """Image model for storing uploaded images"""

    # File information
    image = models.ImageField(upload_to=generate_filename, max_length=255)
    original_filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    file_hash = models.CharField(max_length=64, unique=True, db_index=True)

    # Image properties
    width = models.IntegerField()
    height = models.IntegerField()
    mime_type = models.CharField(max_length=50)

    # Metadata
    upload_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Statistics
    view_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['file_hash']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.created_at})"

    @property
    def url(self):
        """Get full URL for the image"""
        return f"{settings.MEDIA_URL}{self.image.name}"

    @property
    def full_url(self):
        """Get absolute URL for the image - requires request context or domain setting"""
        # This will be constructed dynamically in views with request context
        return self.url

    @property
    def size_kb(self):
        """Get file size in KB"""
        return round(self.file_size / 1024, 2)

    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    @staticmethod
    def calculate_hash(file_content):
        """Calculate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()

    @staticmethod
    def compress_image(image_file, quality=85, max_dimension=4096):
        """Compress image if needed"""
        try:
            img = PILImage.open(image_file)

            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background

            # Resize if too large
            if max(img.size) > max_dimension:
                img.thumbnail((max_dimension, max_dimension), PILImage.Resampling.LANCZOS)

            # Compress
            output = BytesIO()
            img_format = 'JPEG' if image_file.content_type in ['image/jpeg', 'image/jpg'] else 'PNG'
            img.save(output, format=img_format, quality=quality, optimize=True)
            output.seek(0)

            return InMemoryUploadedFile(
                output, 'ImageField',
                f"{os.path.splitext(image_file.name)[0]}.{img_format.lower()}",
                f'image/{img_format.lower()}',
                output.getbuffer().nbytes,
                None
            ), img.size
        except Exception as e:
            raise ValueError(f"Image processing failed: {str(e)}")


class UploadToken(models.Model):
    """API Token model for authentication"""

    token = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=100, help_text="Token name/description")
    is_active = models.BooleanField(default=True)

    # Statistics
    upload_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.token[:16]}..."

    @staticmethod
    def generate_token():
        """Generate a random token"""
        return hashlib.sha256(uuid.uuid4().bytes).hexdigest()

    def record_use(self):
        """Record token usage"""
        self.upload_count += 1
        self.last_used = datetime.now()
        self.save(update_fields=['upload_count', 'last_used'])
