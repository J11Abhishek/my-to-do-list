
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .forms import TaskForm
from .models import Task



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

    task.is_completed = not task.is_completed
    task.save(update_fields=["is_completed", "updated_at"])

    message = (
        "Task marked as completed."
        if task.is_completed
        else "Task marked as pending."
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "title": task.title,
            "is_completed": task.is_completed,
            "message": message,
        })

    messages.success(request, message)
    return redirect("tasks:task_list")


