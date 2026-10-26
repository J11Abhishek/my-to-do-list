
import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .forms import TaskForm
from .models import Task

logger = logging.getLogger(__name__)



def task_list(request):
    tasks = Task.objects.order_by("-created_at")
    total_count = tasks.count()
    completed_count = tasks.filter(is_completed=True).count()
    pending_count = total_count - completed_count

    return render(
        request,
        "tasks/task_list.html",
        {
            "tasks": tasks,
            "total_count": total_count,
            "completed_count": completed_count,
            "pending_count": pending_count,
        },
    )


def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Task created successfully!")
            return redirect("tasks:task_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = TaskForm()

    return render(
        request,
        "tasks/task_form.html",
        {"form": form, "page_title": "Add Task"},
    )


def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect("tasks:task_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = TaskForm(instance=task)

    return render(
        request,
        "tasks/task_form.html",
        {"form": form, "page_title": "Edit Task", "task": task},
    )


def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted successfully!")
        return redirect("tasks:task_list")

    return render(
        request,
        "tasks/task_confirm_delete.html",
        {"task": task},
    )



@require_POST
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    was_completed = task.is_completed
    task.is_completed = not was_completed
    task.save(update_fields=["is_completed", "updated_at"])

    email_status = "not_applicable"
    if task.is_completed and not was_completed:
        if task.notification_email:
            try:
                sent_count = send_mail(
                    subject=f"Task completed: {task.title}",
                    message=(
                        f"Hello,\n\nYour task has been marked as completed:\n\n"
                        f"{task.title}\n"
                        f"{task.description}\n\n"
                        "Well done!"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[task.notification_email],
                    fail_silently=False,
                )
                email_status = "sent" if sent_count else "failed"
            except Exception:
                logger.exception(
                    "Failed to send completion email for task %s", task.pk
                )
                email_status = "failed"
        else:
            email_status = "no_recipient"

    if task.is_completed:
        message = "Task marked as completed."
        if email_status == "sent":
            message += " Email notification sent."
        elif email_status == "no_recipient":
            message += " No notification email is configured for this task."
        elif email_status == "failed":
            message += " The email notification could not be sent."
    else:
        message = "Task marked as pending."

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "title": task.title,
            "is_completed": task.is_completed,
            "message": message,
            "email_notification": email_status,
        })

    if email_status == "failed":
        messages.warning(request, message)
    else:
        messages.success(request, message)
    return redirect("tasks:task_list")
