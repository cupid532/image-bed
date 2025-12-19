"""
User authentication views for email-based registration and login
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import re


def is_valid_password(password):
    """
    Validate password strength
    - At least 8 characters
    - Contains at least one letter and one number
    """
    if len(password) < 8:
        return False, "密码至少需要8个字符"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    return True, ""


def login_page(request):
    """Display login page"""
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'auth/login.html')


def register_page(request):
    """Display registration page"""
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'auth/register.html')


@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    """Handle user registration"""
    try:
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Validate email
        if not email:
            return JsonResponse({'success': False, 'error': '邮箱不能为空'}, status=400)

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'error': '邮箱格式不正确'}, status=400)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': '该邮箱已被注册'}, status=400)

        if User.objects.filter(username=email).exists():
            return JsonResponse({'success': False, 'error': '该邮箱已被注册'}, status=400)

        # Validate password
        if password != password_confirm:
            return JsonResponse({'success': False, 'error': '两次密码输入不一致'}, status=400)

        is_valid, error_msg = is_valid_password(password)
        if not is_valid:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)

        # Create user (use email as username)
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            # Auto login after registration
            login(request, user)

            return JsonResponse({
                'success': True,
                'message': '注册成功！',
                'redirect': '/'
            })

        except IntegrityError:
            return JsonResponse({'success': False, 'error': '注册失败，该邮箱可能已被使用'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'注册失败: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """Handle user login"""
    try:
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', 'off') == 'on'

        if not email or not password:
            return JsonResponse({'success': False, 'error': '邮箱和密码不能为空'}, status=400)

        # Authenticate (using email as username)
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Set session expiry
            if not remember:
                request.session.set_expiry(0)  # Session expires when browser closes
            else:
                request.session.set_expiry(1209600)  # 2 weeks

            return JsonResponse({
                'success': True,
                'message': '登录成功！',
                'redirect': '/'
            })
        else:
            return JsonResponse({'success': False, 'error': '邮箱或密码错误'}, status=401)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'登录失败: {str(e)}'}, status=500)


@require_http_methods(["POST", "GET"])
def logout_user(request):
    """Handle user logout"""
    logout(request)
    return redirect('login_page')


@login_required
def user_profile(request):
    """Display user profile and their uploaded images"""
    user_images = request.user.images.all()

    # Calculate statistics
    total_images = user_images.count()
    total_views = sum(img.view_count for img in user_images)
    total_size = sum(img.file_size for img in user_images)
    total_size_mb = round(total_size / (1024 * 1024), 2)

    context = {
        'user': request.user,
        'images': user_images[:12],  # Show latest 12 images
        'total_images': total_images,
        'total_views': total_views,
        'total_size_mb': total_size_mb,
    }

    return render(request, 'auth/profile.html', context)
