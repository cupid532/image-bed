"""
WSGI config for image_bed project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_bed.settings')

application = get_wsgi_application()
