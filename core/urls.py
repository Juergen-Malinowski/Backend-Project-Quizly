"""URL configuration for the Quizly backend project."""


from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('quizzes_app.api.urls')),
]
