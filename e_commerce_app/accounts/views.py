from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import authenticate
from .jwt_utils import generate_tokens


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistrationForm()

    context = {
        "form": form
    }

    return render(request, "register.html", context)




def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                access_token, refresh_token = generate_tokens(user)

                response = redirect("home")

                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    samesite="Lax",
                    secure=True,  # True in production
                )

                response.set_cookie(
                    key="refresh_token",
                    value=refresh_token,
                    httponly=True,
                    samesite="Lax",
                    secure=True,  # True in production
                    max_age=60 * 15,
                )

                return response

            form.add_error(
                None,
                "Invalid username or password."
            )

    else:
        form = LoginForm()

    return render(
        request,
        "login.html",
        {"form": form}
    )

def logout_view(request):
    response = redirect("home")

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response