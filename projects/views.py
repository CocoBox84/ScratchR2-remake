import os
import re
import json
from django.db.models import Q
from django.shortcuts import render
from .models import Project
import logging
from django.conf import settings
from django.utils.timezone import now
from django.http import (
    HttpResponseNotAllowed, JsonResponse, HttpResponse, HttpResponseBadRequest,
    HttpResponseNotFound, FileResponse
)
from django.http import HttpResponse, Http404
import os
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Project
from .models import BackpackItem
from django.contrib import admin
from django.urls import path, re_path
from itertools import groupby
from django.utils.timezone import localdate
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import Project

from datetime import datetime

logger = logging.getLogger(__name__)
from django.shortcuts import get_object_or_404, render, redirect

import base64

import re

from django.db import models
from django.contrib.auth.models import User

from django.db.models import Count

# --- Core Project Handlers ---

def generate_unique_title(user, base_title):

    # Get all titles that start with the base title
    existing = Project.objects.filter(owner=user, title__startswith=base_title)

    # If no exact match, return base title
    if not existing.filter(title=base_title).exists():
        return base_title

    # Count how many duplicates exist
    count = existing.filter(title__regex=rf"^{base_title}-\d+$").count()
    return f"{base_title}-{count + 1}"

SAFE_ASSET_RE = re.compile(r'[^A-Za-z0-9\.\-_]')

def clean_asset_id(asset_id: str) -> str:
    # keep only hex digits + dot + extension
    newID = re.sub(r'[^0-9a-fA-F].', '', asset_id); print(newID)
    return newID

@csrf_exempt
def new_project_set(request):
    if request.method != 'POST':
        return JsonResponse({"ok": False}, status=405)

    title = request.GET.get("title", "Untitled")
    is_remix = request.GET.get("is_remix")
    is_copy = request.GET.get("is_copy")
    original_id = request.GET.get("original_id")
    unique_title = generate_unique_title(request.user if request.user.is_authenticated else None, title)

    proj = None

    if is_remix == "1" and original_id:
        old_project = get_object_or_404(Project, pk=original_id)
        old_project.remixes = old_project.remixes + 1
        old_project.save(update_fields=["remixes"])

        proj = Project.objects.create(
            title=generate_unique_title(request.user if request.user.is_authenticated else None, f"{title} remix"),
            owner=request.user if request.user.is_authenticated else None,
            data=request.body,
            updated_at=now().strftime('%Y-%m-%d'),
            created_at=now().strftime('%Y-%m-%d'),
            shared_at="Unshared",
            parent=old_project,   # 👈 link to parent
        )
        # optionally copy thumbnail:
        # proj.thumbnail = old_project.thumbnail
        # proj.save(update_fields=["thumbnail"])

    elif is_copy == "1" and original_id:
        old_project = get_object_or_404(Project, pk=original_id)
        proj = Project.objects.create(
            title=generate_unique_title(request.user if request.user.is_authenticated else None, f"{title} copy"),
            owner=request.user if request.user.is_authenticated else None,
            data=request.body,
            updated_at=now().strftime('%Y-%m-%d'),
            created_at=now().strftime('%Y-%m-%d'),
            shared_at="Unshared",
            parent=old_project,   # 👈 copies can also link back if you want
        )

    else:
        proj = Project.objects.create(
            title=unique_title,
            owner=request.user if request.user.is_authenticated else None,
            data=request.body,
            updated_at=now().strftime('%Y-%m-%d'),
            created_at=now().strftime('%Y-%m-%d'),
            shared_at="Unshared"
        )

    encoded_title = base64.b64encode(proj.title.encode('utf-8')).decode('utf-8')

    return JsonResponse({
        "status": "ok",
        "autosave-interval": 120,
        "content-title": encoded_title,
        "content-name": str(proj.id)
    })


'''@csrf_exempt
def set_project_data(request, project_id):
    print("set method called")
    if request.method != 'POST':
        print("Not a post method")
        return JsonResponse({"ok": False}, status=405)
    
    proj = Project.objects.create(
        title=request.GET.get("title", "Untitled"),
        data=request.body
    )

    print("goes down here!")
    return JsonResponse({
    "status": "ok",
    "autosave-interval": 120,
    "content-title": base64.b64encode(proj.title.encode("utf-8")).decode("utf-8"),
    "content-name": str(proj.id)
})

    #return HttpResponse("true", status=200)'''

@csrf_exempt
def save_project(request, project_id=None):
    if request.method != 'POST':
        return HttpResponseNotAllowed(["POST"])

    # Title comes from query string, not the JSON body
    title = request.GET.get("title", "Untitled")

    if not project_id:  # first save, no ID yet
        proj = Project.objects.create(
            title=title,
            owner=request.user,
            data=request.body,
            updated_at = datetime.now().strftime('%Y-%m-%d'),
        )
    else:  # update existing
        proj = get_object_or_404(Project, pk=project_id)
        proj.data = request.body
        proj.title = proj.title
        proj.updated_at = datetime.now().strftime('%Y-%m-%d')
        proj.save()

    encoded_title = base64.b64encode(proj.title.encode("utf-8")).decode("utf-8")

    return JsonResponse({
        "status": "ok",
        "autosave-interval": 120,
        "content-title": encoded_title,
        "content-name": str(proj.id)
    })

@csrf_exempt
def rename_project(request, project_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    proj = get_object_or_404(Project, pk=project_id)
    try:
        data = json.loads(request.body.decode("utf-8"))
        new_title = generate_unique_title(request.user, data.get("title"))
        if new_title:
            proj.updated_at = datetime.now().strftime('%Y-%m-%d')
            proj.title = new_title
            proj.save()
            return JsonResponse({"status": "ok", "title": new_title})
        return JsonResponse({"status": "ok", "title": proj.title})
    except Exception:
        pass

    return JsonResponse({"status": "ok"})


@csrf_exempt
def set_project_thumbnail(request, project_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    proj = get_object_or_404(Project, pk=project_id)

    # Save the raw PNG data into a file field or manually
    thumb_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{project_id}.png")
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)

    with open(thumb_path, "wb") as f:
        f.write(request.body)

    # If your Project model has a FileField/ImageField for thumbnails:
    proj.thumbnail.name = f"thumbnails/{project_id}.png"
    proj.save()

    return JsonResponse({"status": "ok"})



# --- Metadata & Session ---

'''@csrf_exempt
def session_info(request):
    return JsonResponse({
        "user": {
            "username": "ScratchUser206826",
            "id": 1,
            "permissions": {"Scratchers": "true", "student": "true"}
        }
    })'''


@csrf_exempt
def get_preferred_language(request):
    return JsonResponse({"status": "ok", "lang": "en"})
    '''print(request.user.preferred_language)
    if request.user:
        return JsonResponse({"status": "ok", "lang": request.user.preferred_language})
    return JsonResponse({"status": "ok", "lang": "crack"})'''

@csrf_exempt
def set_preferred_language(request):
    language = request.GET.get("lang", "en")
    if request.user:
        request.user.preferred_language = language
    print(language)
    return JsonResponse({"status": "ok", "lang": request.user.preferred_language})

@csrf_exempt
def get_language_list(request):
    return HttpResponse("""
crack, Scratch on Crack
ab,Аҧсшәа
ar,العربية
an,Aragonés
ast,Asturianu
id,Bahasa Indonesia
ms,Bahasa Melayu
be,Беларуская
bg,Български
ca,Català
cs,Česky
cy,Cymraeg
da,Dansk
de,Deutsch
yum,Edible Scratch
et,Eesti
el,Ελληνικά
en,English
eo,Esperanto
es,Español
eu,Euskara
fa,فارسی
fr,Français
fur,Furlan
ga,Gaeilge
gd,Gàidhlig
gl,Galego
ko,한국어
hy,Հայերեն
he,עִבְרִית
hi,हिन्दी
hr,Hrvatski
zu,isiZulu
is,Íslenska
it,Italiano
kn,ಭಾಷೆ-ಹೆಸರು
kk,Қазақша
rw,Kinyarwanda
ht,Kreyòl
ku,Kurdî
la,Latina
lv,Latviešu
lt,Lietuvių
mk,Македонски
hu,Magyar
ml,മലയാളം
mt,Malti
mr,मराठी
cat,Meow
mn,Монгол хэл
my,မြန်မာဘာသာ
nl,Nederlands
ja,日本語
ja-hr,にほんご
nb,Norsk Bokmål
nn,Norsk Nynorsk
uz,Oʻzbekcha
th,ไทย
pl,Polski
pt,Português
pt-br,Português Brasileiro
ro,Română
ru,Русский
sc,Sardu
sq,Shqip
sk,Slovenčina
sl,Slovenščina
sr,Српски
fi,Suomi
sv,Svenska
te,తెలుగు
nai,Tepehuan
vi,Tiếng Việt
tr,Türkçe
uk,Українська
zh-cn,简体中文
zh-tw,正體中文
""")

@csrf_exempt
def get_lang_file(request, langfile):
    import os
    from pathlib import Path
    theFile = os.path.join(Path(__file__).parent.parent, "static", "languages", f"{langfile}")
    print(f"File path {theFile}")
    print(theFile)
    try:
        text = ""
        with open(theFile, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        f.close()
        return HttpResponse(text)
    except Exception as e:
        print(e)
        return HttpResponse("No lang")

@csrf_exempt
def project_meta(request, proj_id):
    return JsonResponse({
        "status": "ok",
        "id": proj_id,
        "title": f"Local Project {proj_id}",
        "creator": "LocalUser",
        "description": "A test project hosted locally",
        "modified": "2025-08-20T20:00:00Z"
    })

@csrf_exempt
def swf_settings(request):
    print("Getting settings")
    return JsonResponse({"status": "ok","autosave_interval": 120,
    "status": "ok",
        "flags": {},
        "permissions": {
            "educator": "true",
            "student": "true",
        },
        "user": {
            "user_admin": True,
        "user_groups": ["Scratchers"],
        "user_is_authenticated": True,
        "user_is_social": True,
                            "permissions": {
            "educator": "true",
            "student": "true"
        }
        },
        "cloud_data_enabled": True,
        "user_admin": True,
        "user_groups": ["Scratchers"],
        "user_is_authenticated": True,
        "user_is_social": True
    })

@csrf_exempt
def get_session(request=""):
    print("Getting session.")
    return JsonResponse({
        "status": "ok",
        "flags": {},
                "permissions": {
            "educator": "true",
            "student": "true",
        },
        "user": {
            "user_admin": True,
        "user_groups": ["Scratchers"],
        "user_is_authenticated": True,
        "user_is_social": True
        },
        "cloud_data_enabled": True,
        "user_admin": True,
        "user_groups": ["Scratchers", "Student", "student", "educator", "Educator"],
        "user_is_authenticated": True,
        "user_is_social": True
    })

# Backpack

@login_required
def backpack_get(request, username):
    if request.user.username != username:
        return JsonResponse([], safe=False)  # don’t leak others’ backpacks
    items = BackpackItem.objects.filter(owner=request.user).order_by("-created_at")
    return JsonResponse([i.as_dict() for i in items], safe=False)

'''@login_required
def backpack_get(request, username):
    if request.user.username != username:
        return JsonResponse([], safe=False)  # don’t leak others’ backpacks
    items = BackpackItem.objects.filter(owner=request.user).order_by("-created_at")
    return JsonResponse([i.as_dict() for i in items], safe=False)'''

@csrf_exempt
@login_required
def backpack_set(request, username):
    if request.user.username != username:
        return HttpResponse("forbidden", status=403)
    try:
        items = json.loads(request.body.decode("utf-8"))
    except Exception:
        items = []

    BackpackItem.objects.filter(owner=request.user).delete()

    for item in items:
        BackpackItem.objects.create(
            owner=request.user,
            type=item.get("type", "sprite"),
            name=item.get("name", "Unnamed"),
            asset_id=item.get("md5", ""),
            data=item.get("body") or None,
            scripts=item.get("scripts") or None,
        )
    return HttpResponse("ok")

@csrf_exempt
@login_required
def log_add_item_to_backpack(request):
    # You can log or ignore
    return HttpResponse("ok")

@csrf_exempt
@login_required
def log_delete_item_from_backpack(request):
    return HttpResponse("ok")

@csrf_exempt
def log_use_item_from_backpack(request):
    return HttpResponse("ok")

# --- Asset Handling ---

@csrf_exempt
def asset_set(request, asset_id):
    print(f"Raw asset id: {asset_id}")
    assetExt = asset_id.split('.')[-1]
    asset_id = clean_asset_id(asset_id) + "." + assetExt

    if request.method != 'POST':
        return HttpResponse(status=405)

    cleaned_id = SAFE_ASSET_RE.sub('', asset_id)
    assets_dir = os.path.join(settings.MEDIA_ROOT, 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    file_path = os.path.join(assets_dir, cleaned_id)

    # Stream the request body in chunks instead of loading it all into memory
    with open(file_path, 'wb') as f:
        for chunk in request:
            f.write(chunk)

    return HttpResponse("true", content_type="text/plain")

@csrf_exempt
def asset_get(request, asset_id):
    assetExt = asset_id.split('.')[-1]
    asset_id = clean_asset_id(asset_id) + "." + assetExt
    print(asset_id)
    file_path = os.path.join(settings.MEDIA_ROOT, 'assets', asset_id)
    if not os.path.exists(file_path):
        return HttpResponseNotFound("asset not found")
    
    print("Getting asset")

    ext = asset_id.lower().split('.')[-1]
    content_type = {
        'svg': 'image/svg+xml',
        'png': 'image/png',
        'wav': 'audio/wav',
        'mp3': 'audio/mpeg'
    }.get(ext, 'application/octet-stream')

    with open(file_path, 'rb') as f:
        return HttpResponse(f.read())
    
@csrf_exempt
def get_asset(request, asset_id):
    """
    Serve an asset file (SVG, PNG, WAV, MP3) from MEDIA_ROOT/assets/<asset_id>.
    """
    assetExt = asset_id.split('.')[-1]
    asset_id = clean_asset_id(asset_id) + "." + assetExt
    print(asset_id)
    file_path = os.path.join(settings.MEDIA_ROOT, 'assets', asset_id)
    if not os.path.exists(file_path):
        return HttpResponseNotFound("asset not found")
    
    print("Getting asset")

    ext = asset_id.lower().split('.')[-1]
    content_type = {
        'svg': 'image/svg+xml',
        'png': 'image/png',
        'wav': 'audio/wav',
        'mp3': 'audio/mpeg'
    }.get(ext, 'application/octet-stream')

    with open(file_path, 'rb') as f:
        return HttpResponse(f.read())

@csrf_exempt
def project_json(request, proj_id):
    project_path = os.path.join(settings.STATIC_ROOT, f'projects/{proj_id}.json')
    if os.path.exists(project_path):
        return FileResponse(open(project_path, 'rb'), content_type='application/json')
    return JsonResponse({"error": "Project not found"}, status=404)


@csrf_exempt
def crossdomain_policy(request):
    xml = """<?xml version="1.0"?>
<!DOCTYPE cross-domain-policy SYSTEM "http://www.macromedia.com/xml/dtds/cross-domain-policy.dtd">
<cross-domain-policy>
  <allow-access-from domain="*" secure="false"/>
</cross-domain-policy>"""
    return HttpResponse(xml, content_type="application/xml")

@csrf_exempt
def project_run(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    if proj.isShared == "true":
        proj.views = proj.views + 1
        proj.save()
    return JsonResponse({"status": "ok"})

@csrf_exempt
def project_page(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    print(project) # Prints it unescaped
    return render(request, "project.html", {"project": project})

@csrf_exempt
def editor_page(request):
    project = {"id": "no", "title": None, "owner": {"username": request.user.username}, "isShared": "false"}
    return render(request, "project.html", {"project": project})


@csrf_exempt
def get_project(request, pid, token):
    print(f"Geting project with id: {pid}")
    proj = get_object_or_404(Project, pk=pid)
    print("Got project")
    print()
    # For now, ignore the token or validate it if you want
    if not proj.data:
        print("empty project")
        return HttpResponse("{}", content_type="application/json")
    print("Responded with saved data.")
    print(proj.isShared)
    return HttpResponse(proj.data, content_type="application/json")

'''@csrf_exempt
def share_project(request, project_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    proj = get_object_or_404(Project, pk=project_id)
    try:
        data = json.loads(request.body.decode("utf-8"))
        isShared = data.get("shareStatus")
        print(f"Share status: {isShared}")
        proj.isShared = isShared != "true"
        proj.updated_at = datetime.now().strftime('%Y-%m-%d')
        proj.shared_at = datetime.now().strftime('%Y-%m-%d')
        proj.save()
    except Exception:
        pass

    return JsonResponse({"status": "ok"})'''

from .models import Message

@csrf_exempt
def toggle_love(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "login_required"}, status=401)

    proj = get_object_or_404(Project, pk=project_id)

    if request.user in proj.loves.all():
        proj.loves.remove(request.user)
        loved = False
    else:
        proj.loves.add(request.user)
        loved = True
        # create a message for the project owner
        if proj.owner != request.user:
            Message.objects.create(
                recipient=proj.owner,
                actor=request.user,
                project=proj,
                type="love"
            )

    return JsonResponse({"ok": True, "loved": loved, "count": proj.love_count()})


@csrf_exempt
def toggle_favorite(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse({"ok": False, "error": "login_required"}, status=401)

    proj = get_object_or_404(Project, pk=project_id)

    if request.user in proj.favorites.all():
        proj.favorites.remove(request.user)
        favorited = False
    else:
        proj.favorites.add(request.user)
        favorited = True
        # create a message for the project owner
        if proj.owner != request.user:
            Message.objects.create(
                recipient=proj.owner,
                actor=request.user,
                project=proj,
                type="favorite"
            )

    return JsonResponse({"ok": True, "favorited": favorited, "count": proj.favorite_count()})

@csrf_exempt
def update_project_info(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        import json
        data = json.loads(request.body.decode("utf-8"))
        proj.instructions = data.get("instructions", proj.instructions)
        proj.notes = data.get("notes", proj.notes)
        proj.updated_at = datetime.now().strftime('%Y-%m-%d')
        proj.save()
        return JsonResponse({"ok": True})
    return JsonResponse({"ok": False}, status=405)

# My stuff routes

@csrf_exempt
def share_project(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    proj.isShared = "true"
    proj.shared_at = datetime.now().strftime('%Y-%m-%d')
    proj.updated_at = datetime.now().strftime('%Y-%m-%d')
    proj.save(update_fields=["isShared", "updated_at", "shared_at"])
    return redirect("mystuff")

@csrf_exempt
def unshare_project(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    proj.isShared = "false"
    proj.save(update_fields=["isShared"])
    return redirect("mystuff")

@csrf_exempt
def delete_project(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    if proj.isTrashed == "true":
        proj.isTrashed = "false"
    else:
        proj.isTrashed = "true"
    proj.save(update_fields=["isTrashed"])   # <-- this actually persists the change
    return redirect("mystuff")

@csrf_exempt
def permanently_delete(request, project_id):
    proj = get_object_or_404(Project, pk=project_id, owner=request.user)
    proj.delete()
    return redirect("mystuff")

# Remix tree

def remix_tree(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    # climb up to ancestors
    ancestors = []
    p = project.parent
    while p:
        ancestors.append(p)
        p = p.parent

    # get descendants (children, grandchildren, etc.)
    def collect_descendants(node):
        result = []
        for child in node.children.all():
            result.append(child)
            result.extend(collect_descendants(child))
        return result

    descendants = collect_descendants(project)

    return render(request, "remix_tree.html", {
        "project": project,
        "ancestors": ancestors,
        "descendants": descendants,
    })

def remix_tree_json(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    def serialize(node):
        return {
            "id": node.id,
            "title": node.title,
            "thumbnail_url": node.thumbnail.url if node.thumbnail else None,
            "children": [serialize(child) for child in node.children.all()]
        }

    return JsonResponse(serialize(project))

from django.db.models import Q
from django.shortcuts import render
from .models import Project

def search_projects(request):
    query = request.GET.get("q", "")
    sort = request.GET.get("sort", "newest")  # default sort

    results = Project.objects.filter(isTrashed="false", isShared="true")

    if query:
        results = results.filter(
            Q(title__icontains=query) |
            Q(owner__username__icontains=query) |
            Q(notes__icontains=query) |
            Q(instructions__icontains=query)
        )

    # Sorting logic
    if sort == "newest":
        results = results.order_by("-created_at")
    elif sort == "views":
        results = results.order_by("-views")
    elif sort == "loves":
        results = results.annotate(love_count=models.Count("loves")).order_by("-love_count")

    results = results[:50]  # limit results

    return render(request, "search_projects.html", {
        "query": query,
        "results": results,
        "sort": sort,
    })

def search_users(request):
    query = request.GET.get("q", "")
    results = []
    if query:
        results = User.objects.filter(
            Q(username__icontains=query)
        )[:50]

    return render(request, "search_users.html", {
        "query": query,
        "results": results,
    })

def search(request):
    tab = request.GET.get("type", "projects")  # projects | users | studios
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "newest")   # newest | views | loves

    context = {"tab": tab, "query": query, "sort": sort}

    if tab == "projects":
        qs = Project.objects.filter(isTrashed="false", isShared="true")
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(owner__username__icontains=query) |
                Q(notes__icontains=query) |
                Q(instructions__icontains=query)
            )

        if sort == "newest":
            qs = qs.order_by("-created_at", "-id")
        elif sort == "views":
            qs = qs.order_by("-views", "-id")



        elif sort == "loves":
            qs = qs.annotate(love_count=Count("loves")).order_by("-love_count", "-id")

        context["results"] = qs[:50]

    elif tab == "users":
        qs = User.objects.all()
        if query:
            qs = qs.filter(username__icontains=query)
        context["results"] = qs[:50]

    elif tab == "studios":
        # Placeholder: if you add a Studio model later, populate here.
        context["results"] = []

    return render(request, "search.html", context)




# Profile pages

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    projects = Project.objects.filter(owner=user, isTrashed="false", isShared="true")
    return render(request, "user_profile.html", {
        "profile_user": user,
        "projects": projects,
    })


# Explore

def explore(request, content_type="projects", category="all"):
    sort = request.GET.get("sort", "featured")
    date = request.GET.get("date", "this_month")

    if content_type == "projects":
        qs = Project.objects.filter(isTrashed="false", isShared="true")

        if category != "all" and category != "featured":
            qs = qs.filter(category=category)

        # Sorting
        if sort == "featured":
            qs = qs.order_by("-id")
        elif sort == "views":
            qs = qs.order_by("-views", "-id")
        elif sort == "loves":
            qs = qs.annotate(love_count=Count("loves")).order_by("-love_count", "-id")
        elif sort == "remixes":
            qs = qs.order_by("-remixes", "-id")
        elif sort == "newest":
            qs = qs.order_by("-created_at", "-id")

        items = qs[:60]

    else:  # studios placeholder
        items = []

    return render(request, "explore.html", {
        "content_type": content_type,
        "category": category,
        "sort": sort,
        "date": date,
        "items": items,
    })

@login_required
def messages_list(request, tab="all"):
    qs = request.user.messages.select_related("actor", "project").order_by("-created_at")

    if tab == "comments":
        qs = qs.filter(type="comment")
    elif tab == "alerts":
        qs = qs.filter(type="staff_alert")  # ONLY staff/admin alerts

    # Group by date
    grouped = {}
    for date, items in groupby(qs, key=lambda m: localdate(m.created_at)):
        grouped[date] = list(items)

    # Mark all unread messages as read on visit, only after grouping them and putting the
    # the data into another variable with the unread state. This will make the read/unread
    # feature not useless.
    request.user.messages.filter(read=False).update(read=True)

    return render(request, "messages.html", {
        "grouped_messages": grouped,
        "active_tab": tab,
    })



'''@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        Message.objects.create(
            recipient=instance.project.owner,
            actor=instance.author,
            type="comment",
            text=f"{instance.author.username} commented on your project",
            link=f"/projects/{instance.project.id}/#comments"
        )
'''

from django.http import JsonResponse

# User Authentication

def account_nav_fragment(request):
    if request.user.is_authenticated:
        context = {
            "LOGGED_IN_USER": {
                "model": {
                    "username": request.user.username,
                    "thumbnail_url": request.user.profile.avatar.url if hasattr(request.user, "profile") else "/static/default.png",
                    "profile_url": f"/users/{request.user.username}/",
                    "has_outstanding_email_confirmation": False,
                },
                "options": {
                    "authenticated": True,
                }
            },
            "TEMPLATE_CUES": {
                "confirmed_email": True,
            }
        }
    else:
        context = {
            "LOGGED_IN_USER": {
                "model": None,
                "options": {
                    "authenticated": False,
                }
            },
            "TEMPLATE_CUES": {}
        }
    return JsonResponse(context)

@login_required
def unread_count(request):
    count = request.user.messages.filter(read=False).count()
    return JsonResponse({"unread": count})


# Admin. Keep at bottom

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Message

@staff_member_required
@require_POST
def create_staff_alert(request):
    username = request.POST.get("username")
    title = request.POST.get("title", "")
    text = request.POST.get("text", "")
    link = request.POST.get("link", "")

    recipient = User.objects.get(username=username)
    Message.objects.create(
        recipient=recipient,
        actor=None,  # system
        type="staff_alert",
        title=title,
        text=text,
        link=link,
    )
    return JsonResponse({"ok": True})