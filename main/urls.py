from django.urls import path

from BA_Project import settings
from .views import create_request_view, login_view, main_page_view, signup_view, logout_view, delete_request_view
from django.conf.urls.static import static

urlpatterns = [
    path('', main_page_view, name='main_page'),
    path('main/', main_page_view, name='main_page'),

    path('logout/', logout_view, name='logout'),
    path('edit_request/<str:request_id>/', create_request_view, name='edit_request'),
    path('add_request/', create_request_view, name='add_request'),
    path('create-request/', create_request_view, name='create_request'),
    path('delete_request/<str:request_id>/', delete_request_view, name='delete_request'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
