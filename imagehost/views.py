import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.paginator import Paginator
from .models import Image, UploadToken
from functools import wraps


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_full_url(request, path):
    """Generate full URL from request and path"""
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    return f"{scheme}://{host}{path}"


def token_required(view_func):
    """Decorator to check API token authentication"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not settings.REQUIRE_AUTH:
            return view_func(request, *args, **kwargs)

        # Check for token in header or query parameter
        token = request.headers.get('X-API-Token') or request.GET.get('token') or request.POST.get('token')

        if not token:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        # Validate token
        try:
            upload_token = UploadToken.objects.get(token=token, is_active=True)
            request.upload_token = upload_token
            return view_func(request, *args, **kwargs)
        except UploadToken.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=403)

    return wrapper


def index(request):
    """Home page with upload interface"""
    return render(request, 'index.html', {
        'require_auth': settings.REQUIRE_AUTH,
        'max_size_mb': settings.MAX_UPLOAD_SIZE / (1024 * 1024)
    })


def gallery(request):
    """Gallery page to view all uploaded images"""
    # Check for token if auth is required
    if settings.REQUIRE_AUTH:
        token = request.GET.get('token')
        if not token:
            return HttpResponseForbidden('Token required')
        try:
            UploadToken.objects.get(token=token, is_active=True)
        except UploadToken.DoesNotExist:
            return HttpResponseForbidden('Invalid token')

    images = Image.objects.all()
    paginator = Paginator(images, 24)  # 24 images per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'gallery.html', {
        'page_obj': page_obj,
        'total_images': images.count()
    })


@csrf_exempt
@require_http_methods(["POST"])
@token_required
def upload_image(request):
    """Handle image upload"""
    try:
        # Check if files were uploaded
        if 'images' not in request.FILES:
            return JsonResponse({'error': 'No image file provided'}, status=400)

        uploaded_files = request.FILES.getlist('images')
        if not uploaded_files:
            return JsonResponse({'error': 'No image file provided'}, status=400)

        results = []
        errors = []

        for image_file in uploaded_files:
            try:
                # Validate file type
                if image_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
                    errors.append(f"{image_file.name}: Invalid file type")
                    continue

                # Validate file size
                if image_file.size > settings.MAX_UPLOAD_SIZE:
                    max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
                    errors.append(f"{image_file.name}: File too large (max {max_mb}MB)")
                    continue

                # Read file content for hash calculation
                image_file.seek(0)
                file_content = image_file.read()
                image_file.seek(0)

                # Calculate hash to check for duplicates
                file_hash = Image.calculate_hash(file_content)

                # Check if image already exists
                existing_image = Image.objects.filter(file_hash=file_hash).first()
                if existing_image:
                    results.append({
                        'filename': image_file.name,
                        'url': get_full_url(request, existing_image.url),
                        'size': existing_image.size_kb,
                        'duplicate': True
                    })
                    continue

                # Compress image if enabled
                if settings.ENABLE_IMAGE_COMPRESSION:
                    compressed_file, dimensions = Image.compress_image(
                        image_file,
                        quality=settings.COMPRESSION_QUALITY,
                        max_dimension=settings.MAX_IMAGE_DIMENSION
                    )
                    width, height = dimensions
                else:
                    from PIL import Image as PILImage
                    img = PILImage.open(image_file)
                    width, height = img.size
                    compressed_file = image_file
                    image_file.seek(0)

                # Create image record
                image = Image(
                    image=compressed_file,
                    original_filename=image_file.name,
                    file_size=compressed_file.size if hasattr(compressed_file, 'size') else image_file.size,
                    file_hash=file_hash,
                    width=width,
                    height=height,
                    mime_type=image_file.content_type,
                    upload_ip=get_client_ip(request)
                )
                image.save()

                # Record token usage
                if hasattr(request, 'upload_token'):
                    request.upload_token.record_use()

                results.append({
                    'filename': image_file.name,
                    'url': get_full_url(request, image.url),
                    'size': image.size_kb,
                    'dimensions': f"{width}x{height}",
                    'duplicate': False
                })

            except Exception as e:
                errors.append(f"{image_file.name}: {str(e)}")

        response_data = {'results': results}
        if errors:
            response_data['errors'] = errors

        status_code = 200 if results else 400
        return JsonResponse(response_data, status=status_code)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@token_required
def list_images(request):
    """List all uploaded images with pagination"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))

        images = Image.objects.all()
        paginator = Paginator(images, per_page)
        page_obj = paginator.get_page(page)

        data = {
            'images': [
                {
                    'id': img.id,
                    'filename': img.original_filename,
                    'url': get_full_url(request, img.url),
                    'size': img.size_kb,
                    'dimensions': f"{img.width}x{img.height}",
                    'views': img.view_count,
                    'created_at': img.created_at.isoformat()
                }
                for img in page_obj
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginator.count,
                'pages': paginator.num_pages
            }
        }

        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
@token_required
def delete_image(request, image_id):
    """Delete an image"""
    try:
        image = get_object_or_404(Image, id=image_id)

        # Delete physical file
        if image.image and os.path.exists(image.image.path):
            os.remove(image.image.path)

        # Delete database record
        image.delete()

        return JsonResponse({'message': 'Image deleted successfully'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def serve_image(request, image_path):
    """Serve image file and increment view count"""
    try:
        # Get image from database
        image = Image.objects.filter(image=image_path).first()

        if not image:
            raise Http404("Image not found")

        # Increment view count
        image.increment_view_count()

        # Serve file
        file_path = os.path.join(settings.MEDIA_ROOT, image_path)
        if not os.path.exists(file_path):
            raise Http404("Image file not found")

        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = image.mime_type
        response['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year

        return response

    except Exception as e:
        raise Http404(str(e))
