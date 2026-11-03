from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    path("", auth_views.LoginView.as_view(template_name="registration/login.html", redirect_authenticated_user=True), name="login",),
    path("home/", views.home, name="home"),
    path("submit/", views.submit_ticket, name="submit_ticket"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("my-tickets/", views.my_tickets, name="my_tickets"),
    path("tickets/<int:ticket_id>/close/", views.close_ticket, name="close_ticket"),
    path("tickets/<int:ticket_id>/reopen/", views.reopen_ticket, name="reopen_ticket"),
    path("tickets/<int:ticket_id>/solve/", views.solve_ticket, name="solve_ticket"),
    path("tickets/<int:ticket_id>/", views.ticket_view, name="ticket_view"),
]