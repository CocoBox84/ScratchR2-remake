# accounts/views.py
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt  # use carefully

@csrf_exempt
def api_login(request):
    if request.method == "GET":
    # First check if the user is already logged in, that way it's probably expecting for the user
        if request.user:
            print(f"User is logged in. Username {request.user.username}")
            return JsonResponse({"ok": True, "user": request.user.username, "id": request.user.id})
        else:
            return JsonResponse({"ok": True, "user": None, "id": None})

    if request.method != "POST": return HttpResponseNotAllowed(["POST"])
    # Expect JSON: {"username": "...", "password": "..."}
    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)

    user = authenticate(username=data.get("username"), password=data.get("password"))
    if not user:
        return JsonResponse({"ok": False, "error": "invalid_credentials"}, status=401)

    login(request, user)
    return JsonResponse({"ok": True, "username": user.username, "id": user.id})

@csrf_exempt
def api_logout(request):
    if request.method != "POST": return HttpResponseNotAllowed(["POST"])
    logout(request)
    return JsonResponse({"ok": True})