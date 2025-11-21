from django.shortcuts import render, redirect
from django.contrib.auth.models import User  # For creating users
from django.contrib.auth import authenticate, login, logout  # For login system
from django.contrib.auth.decorators import login_required  # To restrict pages
from .forms import TaskForm
from .models import Task
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Task, ActivityLog



# ---------------- HOME VIEW ----------------
@login_required(login_url='login_user')
def home(request):

    # Get filters from URL
    status_filter = request.GET.get("status", "All")
    sort_option = request.GET.get("sort", "created")
    search_query = request.GET.get("search", "")

    # Fetch tasks of logged-in user
    tasks = Task.objects.filter(user=request.user)

    # Filter by status
    if status_filter != "All":
        tasks = tasks.filter(status=status_filter)

    # Search by title or description
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Sort tasks
    if sort_option == "created":
        tasks = tasks.order_by('-created_at')
    else:
        tasks = tasks.order_by('deadline')

    # PAGINATION (5 per page)
    paginator = Paginator(tasks, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Dashboard numbers
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status="Completed").count()
    pending_tasks = Task.objects.filter(user=request.user, status="Pending").count()
    inprogress_tasks = Task.objects.filter(user=request.user, status="In Progress").count()

    #  Activity Timeline (correct position)
    activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:5]

    return render(request, "home.html", {
        "tasks": page_obj,
        "page_obj": page_obj,

        "status_filter": status_filter,
        "sort_option": sort_option,
        "search_query": search_query,

        # Dashboard numbers
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "inprogress_tasks": inprogress_tasks,

        # Activity timeline
        "activities": activities
    })




# ---------------- REGISTER VIEW ----------------
def register_user(request):
    if request.method == "POST":
        # Get input values from form
        username = request.POST.get("username")
        password = request.POST.get("password")

        #  Create and save user
        user = User.objects.create_user(username=username, password=password)

        #  Automatically log in the newly created user
        login(request, user)

        #  Redirect to home page (dashboard)
        return redirect("home")

    # Show register page for GET request
    return render(request, "register.html")


# ---------------- LOGIN VIEW ----------------
def login_user(request):
    if request.method == "POST":
        # Get form values
        username = request.POST.get("username")
        password = request.POST.get("password")

        #  Verify user credentials
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Login success
            return redirect("home")
        else:
            # Return login page with error message
            return render(request, "login.html", {"error": "Invalid Credentials"})

    # Show login page for GET request
    return render(request, "login.html")


# ---------------- LOGOUT VIEW ----------------
@login_required
def logout_user(request):
    logout(request)
    #  Redirect to login page after logout
    return redirect("login_user")

# ---------------- ADD TASK VIEW ----------------
@login_required
def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()

            #  Log Activity
            ActivityLog.objects.create(
                user=request.user,
                action=f"Created task: {task.title}"
            )

            return redirect('home')
    else:
        form = TaskForm()

    return render(request, 'add_task.html', {'form': form})



# ------------------ EDIT TASK VIEW ------------------
@login_required(login_url='login_user')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()

            # Log activity after editing task
            ActivityLog.objects.create(
                user=request.user,
                action=f"Updated task: {task.title}"
            )

            return redirect('home')
    else:
        form = TaskForm(instance=task)

    return render(request, "edit_task.html", {"form": form})



# ------------------ DELETE TASK VIEW ------------------
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    # Log activity BEFORE deletion
    ActivityLog.objects.create(
        user=request.user,
        action=f"Deleted task: {task.title}"
    )

    task.delete()
    return redirect('home')

# --------------- EDIT TASK VIEW ----------------
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = form.save()

            # Log the edit activity
            ActivityLog.objects.create(
                user=request.user,
                action=f"Updated task: {updated_task.title}"
            )

            return redirect('home')
    else:
        form = TaskForm(instance=task)

    return render(request, "edit_task.html", {"form": form})
