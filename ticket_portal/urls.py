from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    path("", auth_views.LoginView.as_view(template_name="registration/login.html", redirect_authenticated_user=True), name="login",),
    path("submit/", views.submit_ticket, name="submit_ticket"),
    path("tickets/<int:ticket_id>/", views.ticket_view, name="ticket_view"),
]