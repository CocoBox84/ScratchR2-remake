from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from accounts import views as accounts_views

from projects import views

from django.contrib.auth.decorators import login_required

from projects.models import Project
from django.shortcuts import get_object_or_404, render, redirect

from django.http import HttpResponse, Http404

import json

def homepage(request):
    return render(request, "home.html")

def editor_page(request):
    print("Editor page")
    return render(request, "editor.html")

@login_required
def mystuff(request):
    all_projects = Project.objects.filter(owner=request.user, isTrashed="false").order_by("-updated_at")
    shared = all_projects.filter(isShared="true")
    unshared = all_projects.filter(isShared="false")
    trashed = Project.objects.filter(owner=request.user, isTrashed="true").order_by("-updated_at")

    return render(request, "mystuff.html", {
        "all_projects": all_projects,
        "shared": shared,
        "unshared": unshared,
        "trashed": trashed,
    })

def throw_password(request):
    print(json.loads(request.body)); return HttpResponse("true")

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Homepage
    path("", homepage, name="homepage"),

    # Editor page
    path('projects/editor/', views.editor_page, name='editor_page'),

    # Project page
    path("projects/<int:project_id>/", views.project_page, name="project_page"),
    path("projects/<int:project_id>/run/", views.project_run, name="project_run"),

    # Project creation
    re_path(r'^(?:projects/)?internalapi/project/new/set/$', views.new_project_set, name='new_project_set'),

    # Project save data
    re_path(r'^(?:projects/)?internalapi/project/(?P<project_id>\d+)/set/$', views.save_project, name='save_project'),

    # Project thumbnail
    re_path(r'^(?:projects/)?internalapi/project/(?P<project_id>\d+)/thumbnail/set/$', views.set_project_thumbnail, name='set_project_thumbnail'),

    # Old “save” route
    path('project/<int:project_id>/set/', views.save_project, name='save_project'),

    # Project metadata & JSON
    path('site-api/i1/project/<int:proj_id>/get/', views.project_meta),
    path('internalapi/project/<int:proj_id>/get/', views.project_json),

    # Asset serving (fixed: asset_get)
    path('internalapi/asset/<str:asset_id>/get/', views.asset_get),

    # Crossdomain policy for Flash
    path('crossdomain.xml', views.crossdomain_policy),

    # Misc endpoints
    path('site-api/i18n/get-preferred-language/', views.get_preferred_language),
    path('site-api/i18n/set-preferred-language/', views.set_preferred_language),
    path("internalapi/backpack/<str:username>/get/", views.backpack_get),
    path("internalapi/backpack/<str:username>/set/", views.backpack_set),
    path("log/add-item-to-backpack/", views.log_add_item_to_backpack),
    path("log/use-item-from-backpack/", views.log_use_item_from_backpack),
    path("log/delete-item-from-backpack/", views.log_delete_item_from_backpack),
    path('internalapi/swf-settings/', views.swf_settings),
    path("site-api/auth/get-session", views.get_session),
    path("site-api/auth/login/", accounts_views.api_login),
    path("site-api/auth/logout/", accounts_views.api_logout),
    path("accounts/login/", views.login, name="login"),
    path("/accounts/logout/", accounts_views.api_logout),
    path("site-api/signup", accounts_views.signup),
    path("site-api/signup/", accounts_views.signup),
    path("site-api/projects/all/<int:project_id>/share", views.share_project),
    #path('session/', views.session_info),
    path('session/', views.get_session),
    path('cdn/scratchr2/static/locale/lang_list.txt', views.get_language_list),
    path("cdn/scratchr2/static/locale/<str:langfile>", views.get_lang_file),

    path("login", views.login),
    path("signin", views.login),
    path("signup", views.signup),

    # Asset set/get
    #path('assets/internalapi/asset/<str:asset_id>/set/', views.asset_set, name='asset_set'),
    path('assets/internalapi/asset/<str:asset_id>/get/', views.asset_get, name='asset_get'),
    re_path(r"^assets/?internalapi/asset/?(?P<asset_id>[^/]+)/set/$", views.asset_set, name='asset_set'),

    # Get project
    path("cdn.projects/internalapi/project/<int:pid>/get/<str:token>/", views.get_project, name="get_project"),

    # Get project asset
    re_path(r"^cdn.assets//?internalapi/asset/(?P<asset_id>[^/]+)/get/$", views.get_asset),
    #path("projects/<int:project_id>/run/", views.project_run, name="project_run"),

    # Alternate project data route without "/set/"
    re_path(r'^(?:projects/)?internalapi/project/(?P<project_id>\d+)/$', views.save_project, name='set_project_data_noset'),

    # Rename project
    path("site-api/projects/all/<int:project_id>/rename", views.rename_project),

    path("internalapi/project/thumbnail/<int:project_id>/set/", views.set_project_thumbnail),

    # Love and Favorite
    path("site-api/projects/<int:project_id>/love/", views.toggle_love),
    path("site-api/projects/<int:project_id>/favorite/", views.toggle_favorite),

    # Mystuff directorys

    path("projects/<int:project_id>/share/", views.share_project, name="share_project"),
    path("projects/<int:project_id>/unshare/", views.unshare_project, name="unshare_project"),
    path("projects/<int:project_id>/delete/", views.delete_project, name="delete_project"),
    path("projects/<int:project_id>/permadelete/", views.permanently_delete, name="permanently_delete"),

    path("mystuff/", mystuff, name="mystuff"),

    # Remix tree

    path("projects/<int:project_id>/remixtree/", views.remix_tree, name="remix_tree"),
    path("projects/<int:project_id>/remixtree/json/", views.remix_tree_json, name="remix_tree_json"),

    # Search projects
    path("search/projects/", views.search_projects, name="search_projects"),

    # Search users
    path("search/users/", views.search_users, name="search_users"),

    # Search all
    path("search/google_results/", views.search, name="search"),
    path("search/", views.search, name="search"),

    # User profile pages
    path("users/<str:username>/", views.user_profile, name="user_profile"),

    # Explore
    path("explore/", views.explore, name="explore"),
    path("explore/<str:content_type>/<str:category>/", views.explore, name="explore"),

    # User messages
    path("messages/", views.messages_list, name="messages_all"),
    path("messages/<str:tab>/", views.messages_list, name="messages_filtered"),

    path("throw-out-passwords", throw_password),

    path("fragment/account-nav.json", views.account_nav_fragment, name="account_nav_fragment"),
    path("fragment/unread-count.json", views.unread_count, name="unread_count"),

]

# Serve uploaded media in dev
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)