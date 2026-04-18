# accounts/views.py
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.http import (
    HttpResponseNotAllowed, JsonResponse, HttpResponse, HttpResponseBadRequest,
    HttpResponseNotFound, FileResponse
)
from django.views.decorators.csrf import csrf_exempt  # use carefully
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

from django.db.models import Count

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
    isFromForm = False
    import json
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        # If JSON fails, check as a normal form:
        data = request.POST.copy()
        isFromForm = True

    user = authenticate(username=data.get("username"), password=data.get("password"))
    if not user:
        return JsonResponse({"ok": False, "error": "invalid_credentials"}, status=401)

    login(request, user)
    if isFromForm:
        # Check for the "?next=" param
        nextUrl = request.GET.get("next")
        print(nextUrl)
        if nextUrl is not None and nextUrl is not "":
            return redirect(nextUrl)
        else: return redirect("/")
    else:
        return JsonResponse({"ok": True, "username": user.username, "id": user.id})

@csrf_exempt
def api_logout(request):
    if request.method != "POST": return HttpResponseNotAllowed(["POST"])
    logout(request)
    return JsonResponse({"ok": True})

def signup(request):
    if request.method == "GET":
        return render(request, "signup.html")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already taken", status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect("/")

    return HttpResponse(f"'{request.method}' is not allowed here.", status=405)