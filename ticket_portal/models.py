from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
    subject = models.CharField(max_length=250)
    description = models.TextField()
    is_open = models.BooleanField(default=True)

    created_by = models.ForeignKey(User,on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)



class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="replies")
    message = models.TextField()

    created_by = models.ForeignKey(User,on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)