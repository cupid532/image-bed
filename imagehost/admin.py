from django.contrib import admin
from .models import Image, UploadToken


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'size_kb', 'width', 'height', 'view_count', 'created_at', 'upload_ip']
    list_filter = ['created_at', 'mime_type']
    search_fields = ['original_filename', 'file_hash', 'upload_ip']
    readonly_fields = ['file_hash', 'width', 'height', 'file_size', 'created_at', 'view_count', 'upload_ip']
    date_hierarchy = 'created_at'

    def size_kb(self, obj):
        return f"{obj.size_kb} KB"
    size_kb.short_description = 'Size'


@admin.register(UploadToken)
class UploadTokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'token_preview', 'is_active', 'upload_count', 'last_used', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'token']
    readonly_fields = ['token', 'upload_count', 'last_used', 'created_at']

    def token_preview(self, obj):
        return f"{obj.token[:16]}..."
    token_preview.short_description = 'Token'

    def save_model(self, request, obj, form, change):
        if not obj.token:
            obj.token = UploadToken.generate_token()
        super().save_model(request, obj, form, change)
