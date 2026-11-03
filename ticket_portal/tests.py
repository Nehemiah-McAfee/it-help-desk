from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Ticket, TicketReply


class TicketAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="customer", password="pass")
        self.other_user = User.objects.create_user(username="other", password="pass")
        self.staff = User.objects.create_user(
            username="staff",
            password="pass",
            is_staff=True,
        )
        self.user_ticket = Ticket.objects.create(
            subject="My issue",
            description="Details",
            created_by=self.user,
        )
        self.other_ticket = Ticket.objects.create(
            subject="Another issue",
            description="Details",
            created_by=self.other_user,
        )

    def test_my_tickets_only_shows_current_users_tickets(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_tickets"))

        self.assertContains(response, self.user_ticket.subject)
        self.assertNotContains(response, self.other_ticket.subject)

    def test_ticket_creator_can_view_ticket(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("ticket_view", args=[self.user_ticket.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user_ticket.subject)

    def test_user_cannot_view_another_users_ticket(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("ticket_view", args=[self.other_ticket.pk]),
        )

        self.assertEqual(response.status_code, 404)

    def test_staff_can_view_any_ticket_and_staff_queue(self):
        self.client.force_login(self.staff)

        detail_response = self.client.get(
            reverse("ticket_view", args=[self.other_ticket.pk]),
        )
        list_response = self.client.get(reverse("ticket_list"))

        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, self.other_ticket.subject)
        self.assertContains(list_response, self.user_ticket.subject)
        self.assertContains(list_response, self.other_ticket.subject)
        self.assertNotContains(list_response, "Submit Issue")

    def test_regular_user_sees_submit_issue_navigation(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("my_tickets"))

        self.assertContains(response, "Submit Issue")
        self.assertContains(
            response,
            f'href="{reverse("home")}"',
        )

    def test_staff_brand_link_goes_to_staff_ticket_view(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse("ticket_list"))

        self.assertContains(
            response,
            f'href="{reverse("home")}"',
        )
        self.assertRedirects(
            self.client.get(reverse("home")),
            reverse("ticket_list"),
        )

    def test_regular_user_home_goes_to_my_tickets(self):
        self.client.force_login(self.user)

        self.assertRedirects(
            self.client.get(reverse("home")),
            reverse("my_tickets"),
        )

    def test_ticket_creator_can_reply_to_their_ticket(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("ticket_view", args=[self.user_ticket.pk]),
            {"message": "I can provide more details."},
        )

        self.assertRedirects(
            response,
            reverse("ticket_view", args=[self.user_ticket.pk]),
        )
        reply = TicketReply.objects.get(ticket=self.user_ticket)
        self.assertEqual(reply.created_by, self.user)
        self.assertEqual(reply.message, "I can provide more details.")

    def test_staff_can_reply_to_any_ticket(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("ticket_view", args=[self.other_ticket.pk]),
            {"message": "We are looking into this."},
        )

        self.assertRedirects(
            response,
            reverse("ticket_view", args=[self.other_ticket.pk]),
        )
        reply = TicketReply.objects.get(ticket=self.other_ticket)
        self.assertEqual(reply.created_by, self.staff)

    def test_blank_reply_is_not_saved(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("ticket_view", args=[self.user_ticket.pk]),
            {"message": "   "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a reply before submitting.")
        self.assertFalse(TicketReply.objects.filter(ticket=self.user_ticket).exists())

    def test_staff_can_close_ticket(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("close_ticket", args=[self.user_ticket.pk]),
        )

        self.assertRedirects(
            response,
            reverse("ticket_view", args=[self.user_ticket.pk]),
        )
        self.user_ticket.refresh_from_db()
        self.assertFalse(self.user_ticket.is_open)

    def test_non_staff_cannot_close_ticket(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("close_ticket", args=[self.user_ticket.pk]),
        )

        self.assertEqual(response.status_code, 302)
        self.user_ticket.refresh_from_db()
        self.assertTrue(self.user_ticket.is_open)

    def test_staff_can_reopen_closed_ticket(self):
        self.user_ticket.is_open = False
        self.user_ticket.save(update_fields=["is_open"])
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("reopen_ticket", args=[self.user_ticket.pk]),
        )

        self.assertRedirects(
            response,
            reverse("ticket_view", args=[self.user_ticket.pk]),
        )
        self.user_ticket.refresh_from_db()
        self.assertTrue(self.user_ticket.is_open)

    def test_non_staff_cannot_reopen_closed_ticket(self):
        self.user_ticket.is_open = False
        self.user_ticket.save(update_fields=["is_open"])
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("reopen_ticket", args=[self.user_ticket.pk]),
        )

        self.assertEqual(response.status_code, 302)
        self.user_ticket.refresh_from_db()
        self.assertFalse(self.user_ticket.is_open)

    def test_owner_can_mark_their_ticket_solved(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("solve_ticket", args=[self.user_ticket.pk]),
        )

        self.assertRedirects(
            response,
            reverse("ticket_view", args=[self.user_ticket.pk]),
        )
        self.user_ticket.refresh_from_db()
        self.assertFalse(self.user_ticket.is_open)

    def test_user_cannot_mark_another_users_ticket_solved(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("solve_ticket", args=[self.other_ticket.pk]),
        )

        self.assertEqual(response.status_code, 404)
        self.other_ticket.refresh_from_db()
        self.assertTrue(self.other_ticket.is_open)

    def test_owner_can_view_closed_ticket_without_reply_form(self):
        self.user_ticket.is_open = False
        self.user_ticket.save(update_fields=["is_open"])
        self.client.force_login(self.user)

        list_response = self.client.get(reverse("my_tickets"))
        detail_response = self.client.get(
            reverse("ticket_view", args=[self.user_ticket.pk]),
        )

        self.assertContains(list_response, self.user_ticket.subject)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "This ticket is closed.")
        self.assertNotContains(detail_response, "Send Reply")

    def test_closed_ticket_rejects_replies_from_owner_and_staff(self):
        self.user_ticket.is_open = False
        self.user_ticket.save(update_fields=["is_open"])
        ticket_url = reverse("ticket_view", args=[self.user_ticket.pk])

        for account in (self.user, self.staff):
            with self.subTest(account=account.username):
                self.client.force_login(account)
                response = self.client.post(ticket_url, {"message": "A reply"})

                self.assertEqual(response.status_code, 403)
                self.assertContains(
                    response,
                    "This ticket is closed and cannot receive replies.",
                    status_code=403,
                )

        self.assertFalse(TicketReply.objects.filter(ticket=self.user_ticket).exists())
