"""
ASGI config for image_bed project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_bed.settings')

application = get_asgi_application()
