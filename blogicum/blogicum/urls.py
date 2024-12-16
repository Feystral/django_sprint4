from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler404, handler500

from pages.views import PageNotFoundView
from .views import UserRegistrationView

handler404 = PageNotFoundView.as_view()
handler500 = "pages.views.internal_server_error"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', UserRegistrationView.as_view(),
         name='registration'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
