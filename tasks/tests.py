
from django.test import TestCase
from django.urls import reverse

from .models import Task


class TaskModelTests(TestCase):
    def test_task_defaults(self):
        task = Task.objects.create(title="Learn Django")

        self.assertFalse(task.is_completed)
        self.assertEqual(task.description, "")
        self.assertTrue(task.created_at)
        self.assertTrue(task.updated_at)

    def test_task_string_representation(self):
        task = Task.objects.create(title="Study Python")

        self.assertEqual(str(task), "Study Python")


class TaskViewTests(TestCase):
    def test_homepage_loads(self):
        response = self.client.get(reverse("tasks:task_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Tasks")

    def test_create_task(self):
        response = self.client.post(
            reverse("tasks:task_create"),
            {
                "title": "Finish project",
                "description": "Complete the Django app",
            },
        )

        self.assertRedirects(response, reverse("tasks:task_list"))
        self.assertTrue(
            Task.objects.filter(title="Finish project").exists()
        )

    def test_create_task_rejects_blank_title(self):
        response = self.client.post(
            reverse("tasks:task_create"),
            {"title": "   ", "description": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Task.objects.exists())
        self.assertFormError(
            response.context["form"],
            "title",
            "Please enter a task title.",
        )

    def test_edit_task(self):
        task = Task.objects.create(title="Old title")

        response = self.client.post(
            reverse("tasks:task_update", args=[task.pk]),
            {"title": "New title", "description": "Updated details"},
        )

        self.assertRedirects(response, reverse("tasks:task_list"))

        task.refresh_from_db()
        self.assertEqual(task.title, "New title")
        self.assertEqual(task.description, "Updated details")

    def test_delete_requires_post(self):
        task = Task.objects.create(title="Keep until confirmed")

        response = self.client.get(
            reverse("tasks:task_delete", args=[task.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_delete_task(self):
        task = Task.objects.create(title="Remove me")

        response = self.client.post(
            reverse("tasks:task_delete", args=[task.pk])
        )

        self.assertRedirects(response, reverse("tasks:task_list"))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_toggle_task_with_ajax(self):
        task = Task.objects.create(title="Toggle me")

        response = self.client.post(
            reverse("tasks:task_toggle", args=[task.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertTrue(response.json()["is_completed"])

        task.refresh_from_db()
        self.assertTrue(task.is_completed)

    def test_toggle_rejects_get(self):
        task = Task.objects.create(title="Do not toggle on GET")

        response = self.client.get(
            reverse("tasks:task_toggle", args=[task.pk])
        )

        self.assertEqual(response.status_code, 405)

        task.refresh_from_db()
        self.assertFalse(task.is_completed)

    def test_missing_task_returns_404(self):
        response = self.client.get(
            reverse("tasks:task_update", args=[999999])
        )

        self.assertEqual(response.status_code, 404)
