from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def register_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not all([username, email, password, confirm_password]):
            messages.error(request, "Please fill in all the required fields.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "The passwords you entered do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.warning(request, "This username is already taken. Please choose another one.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.warning(request, "An account with this email already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Your account has been created successfully. You can now sign in."
        )
        return redirect("login")

    return render(request, "accounts/register.html")


def login_user(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please enter your username and password.")
            return redirect("login")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)

            if user.is_staff:
                messages.success(
                    request,
                    f"Welcome back, {user.username}. You are now signed in."
                )
                return redirect("manager_dashboard")

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )
            return redirect("home")

        messages.error(
            request,
            "Invalid username or password. Please check your credentials and try again."
        )

    return render(request, "accounts/login.html")


def logout_user(request):
    logout(request)
    messages.success(
        request,
        "You have been signed out successfully."
    )
    return redirect("home")
