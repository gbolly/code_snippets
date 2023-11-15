from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.create_user, name="user-signup"),
    path('login/', views.login_user, name="user-login"),
    path('modify-password/', views.password_change, name="password-change"),
    path('password-reset/', views.password_reset, name="reset-password"),
    path('password-reset-confirm/', views.password_reset_confirm, name="confirm-reset-password"),
    path('update/', views.update_user, name="user-update"),
]
