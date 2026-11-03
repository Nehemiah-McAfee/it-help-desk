from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import Ticket, TicketReply


@login_required
def home(request):
    destination = "ticket_list" if request.user.is_staff else "my_tickets"
    return redirect(reverse(destination))


@login_required
def submit_ticket(request):
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        description = request.POST.get("description", "").strip()
        action = request.POST.get("action", "").strip()

        if not subject or not description:
            return render(request, "portal/ticket_submission.html", {
                "subject": subject,
                "description": description,
                "error": "Enter both a subject and description of your problem",
            })

        if action == "submit_ticket":
            ticket = Ticket.objects.create(subject=subject, description=description, created_by=request.user)
            if request.user.is_staff:
                return redirect("ticket_view", ticket_id=ticket.id)
            return render(request, "portal/ticket_submission.html", {
                "success": "Your ticket was submitted successfully. You can view and reply to it from My Tickets.",
            })

        elif action == "ai_suggestion":
            return render(request, "portal/ticket_submission.html", {
                "subject": subject,
                "description": description,
                "suggestion": "AI stuff here later",
            })

    return render(request, "portal/ticket_submission.html")


@login_required
@staff_member_required
def ticket_list(request):
    tickets = Ticket.objects.select_related("created_by").order_by("-created_at")
    return render(request, "portal/ticket_list.html", {"tickets": tickets})


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(
        created_by=request.user,
    ).select_related("created_by").order_by("-created_at")
    return render(request, "portal/my_tickets.html", {"tickets": tickets})


@login_required
def ticket_view(request, ticket_id):
    tickets = Ticket.objects.select_related("created_by")
    if not request.user.is_staff:
        tickets = tickets.filter(created_by=request.user)
    ticket = get_object_or_404(tickets, pk=ticket_id)

    error = None
    if request.method == "POST":
        message = request.POST.get("message", "").strip()
        if not ticket.is_open:
            error = "This ticket is closed and cannot receive replies."
        elif not message:
            error = "Enter a reply before submitting."
        else:
            TicketReply.objects.create(
                ticket=ticket,
                message=message,
                created_by=request.user,
            )
            return redirect("ticket_view", ticket_id=ticket.id)

    replies = ticket.replies.select_related("created_by").order_by("created_at")
    return render(request, "portal/ticket_detail.html", {
        "ticket": ticket,
        "replies": replies,
        "error": error,
        "reply_message": request.POST.get("message", "") if error else "",
    }, status=403 if error and not ticket.is_open else 200)


@login_required
@staff_member_required
@require_POST
def close_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if ticket.is_open:
        ticket.is_open = False
        ticket.save(update_fields=["is_open"])
    return redirect("ticket_view", ticket_id=ticket.id)


@login_required
@staff_member_required
@require_POST
def reopen_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if not ticket.is_open:
        ticket.is_open = True
        ticket.save(update_fields=["is_open"])
    return redirect("ticket_view", ticket_id=ticket.id)


@login_required
@require_POST
def solve_ticket(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        pk=ticket_id,
        created_by=request.user,
    )
    if ticket.is_open:
        ticket.is_open = False
        ticket.save(update_fields=["is_open"])
    return redirect("ticket_view", ticket_id=ticket.id)
