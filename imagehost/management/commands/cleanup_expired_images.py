"""
Django management command to clean up expired temporary images
This command should be run periodically via cron
"""

import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from imagehost.models import Image


class Command(BaseCommand):
    help = 'Delete expired temporary images (uploaded by guests)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Find expired images
        now = timezone.now()
        expired_images = Image.objects.filter(
            is_temporary=True,
            expires_at__isnull=False,
            expires_at__lt=now
        )

        count = expired_images.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired images found.'))
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Would delete {count} expired images:')
            )
            for img in expired_images:
                self.stdout.write(f'  - {img.original_filename} (expired at {img.expires_at})')
            return

        # Delete expired images
        deleted_files = 0
        deleted_records = 0
        errors = []

        for img in expired_images:
            try:
                # Delete physical file
                if img.image and os.path.exists(img.image.path):
                    os.remove(img.image.path)
                    deleted_files += 1
                    self.stdout.write(f'Deleted file: {img.image.path}')

                # Delete database record
                img.delete()
                deleted_records += 1

            except Exception as e:
                error_msg = f'Error deleting {img.original_filename}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

        # Summary
        self.stdout.write(self.style.SUCCESS(
            f'\nCleanup completed:'
        ))
        self.stdout.write(f'  - Deleted {deleted_files} files')
        self.stdout.write(f'  - Deleted {deleted_records} database records')

        if errors:
            self.stdout.write(self.style.ERROR(f'  - {len(errors)} errors occurred'))
        else:
            self.stdout.write(self.style.SUCCESS('  - No errors'))
