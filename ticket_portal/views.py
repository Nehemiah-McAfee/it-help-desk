from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Ticket

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
            return redirect("ticket_view", ticket_id=ticket.id)
        
        elif action == "ai_suggestion":
            return render(request, "portal/ticket_submission.html", {
                "subject": subject,
                "description": description,
                "suggestion": "AI stuff here later",
            })

    return render(request, "portal/ticket_submission.html")


def ticket_view(request):
    pass
