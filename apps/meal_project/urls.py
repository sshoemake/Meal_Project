"""meal_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views as user_views
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", user_views.register, name="register"),
    path("profile/", user_views.profile, name="profile"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    # path(
    #     "logout/",
    #     auth_views.LogoutView.as_view(template_name="users/logout.html"),
    #     name="logout",
    # ),
    path(
        "logout/confirm/",
        TemplateView.as_view(template_name="users/logout_confirm.html"),
        name="logout_confirm",
    ),
    # actual logout endpoint — require POST only
    path(
        "logout/",
        require_POST(auth_views.LogoutView.as_view(template_name="users/logout.html")),
        name="logout",
    ),    
    path("", include("apps.meals.urls")),
    path("", include("apps.ingredients.urls")),
    path("", include("apps.carts.urls")),
    path("", include("apps.stores.urls")),
    path("", include("apps.metrics.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
