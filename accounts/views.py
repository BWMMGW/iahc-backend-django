import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import User, Message, Chat
from django.shortcuts import redirect

@require_http_methods(["GET"])
def home(request):
    return JsonResponse({"message": "iahc API"})

@require_http_methods(["GET"])
def check_session(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "authenticated": True,
            "user": {
                "id": request.user.id, 
                "username": request.user.username,
                "email": request.user.email
            }
        })
    return JsonResponse({"authenticated": False})

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    if user.check_password(password):
        login(request, user)
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        return JsonResponse({
            "success": True,
            "user": {"id": user.id, "username": user.username}
        })
    else:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    firstname = data.get('firstname', '').strip()
    lastname = data.get('lastname', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    birthday_str = data.get('birthday', '').strip()
    gender = data.get('gender', '').strip()
    location = data.get('location', '').strip()
    bio = data.get('bio', '').strip()
    picture = data.get('picture', '').strip()

    if not all([firstname, lastname, username, email, password]):
        return JsonResponse({"error": "First name, last name, username, email and password are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    birthday = None
    if birthday_str:
        try:
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({"error": "Invalid birthday format. Use YYYY-MM-DD."}, status=400)

    try:
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            firstname=firstname,
            lastname=lastname,
            birthday=birthday,
            gender=gender if gender else None,
            location=location if location else None,
            bio=bio if bio else None,
            picture=picture if picture else None
        )
    except Exception as e:
        return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)

    return JsonResponse({"success": True, "message": "Account created"}, status=201)

@require_http_methods(["GET"])
def get_profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "username": user.username,
        "birthday": user.birthday.isoformat() if user.birthday else None,
        "gender": user.gender,
        "location": user.location,
        "bio": user.bio,
        "picture": user.picture,
        "created_at": user.created_at
    })

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def edit_profile(request, username):
    if request.user.username != username:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    user = request.user
    user.firstname = data.get('firstname', '').strip() or None
    user.lastname = data.get('lastname', '').strip() or None
    user.location = data.get('location', '').strip() or None
    user.bio = data.get('bio', '').strip() or None
    user.gender = data.get('gender', '').strip() or None
    user.picture = data.get('picture', '').strip() or None

    birthday_str = data.get('birthday', '').strip()
    if birthday_str:
        try:
            user.birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({"error": "Invalid birthday format. Use YYYY-MM-DD."}, status=400)
    else:
        user.birthday = None

    if user.bio and len(user.bio) > 100:
        return JsonResponse({"error": "Bio must be 100 characters or less."}, status=400)

    try:
        user.save()
    except Exception as e:
        return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)

    return JsonResponse({
        "success": True,
        "message": "Profile updated successfully",
        "user": {
            "firstname": user.firstname,
            "lastname": user.lastname,
            "username": user.username,
            "email": user.email,
            "birthday": user.birthday.isoformat() if user.birthday else None,
            "gender": user.gender,
            "location": user.location,
            "bio": user.bio,
            "picture": user.picture
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def recovery_view(request):
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    email = data.get('email')

    if not email:
        return JsonResponse({"error": "Email is required"}, status=400)

    # TODO: Implement actual password reset logic
    return JsonResponse({
        "success": True,
        "message": f"If an account exists for {email}, a reset link will be sent."
    })

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return JsonResponse({"success": True})


# ================== NEW SEARCH ENDPOINT ==================
@login_required
@require_http_methods(["GET"])
def search_users(request):
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({"error": "Search query must be at least 2 characters."}, status=400)

    # Search by username, first name, or last name (case-insensitive)
    results = User.objects.filter(
        username__icontains=query
    ) | User.objects.filter(
        firstname__icontains=query
    ) | User.objects.filter(
        lastname__icontains=query
    )

    # Limit to 20 results for performance
    results = results[:20]

    users_data = []
    for user in results:
        users_data.append({
            "id": user.id,
            "username": user.username,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "picture": user.picture,
        })

    return JsonResponse({"users": users_data})
