from urllib import response
from django.shortcuts import render
from flask import Response
from .forms import UserRegistrationForm
from django.contrib import messages
from .models import UserRegistrationModel
from django.http import HttpResponse
from django.template import RequestContext


# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHome.html', {})
            else:
                messages.success(request, 'Your Account has not been activated by Admin.')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHome.html', {})


from django.conf import settings
import os
import pandas as pd


def viewdata(request):
    movies = os.path.join(settings.MEDIA_ROOT, "leadcopy", "movies.csv")
    rating = os.path.join(settings.MEDIA_ROOT, "leadcopy", "ratings.csv")
    df_m = pd.read_csv(movies, nrows=500)
    df_r = pd.read_csv(rating, nrows=500)
    df_m = df_m.to_html
    df_r = df_r.to_html
    return render(request, "users/views_movies.html", {"df_m": df_m, "df_r": df_r})


def user_collaborating(request):
    if request.method == "POST":
        from .utility.Collaborating_Filter import start_collaborating
        movieName = request.POST.get('movie_name')
        recom_movie = start_collaborating(movieName)
        movies = os.path.join(settings.MEDIA_ROOT, "leadcopy", "movies.csv")
        df_r = pd.read_csv(movies, nrows=100)
        m = df_r.title.unique()
        return render(request, "users/collaborate.html", {"movies": m, "results": recom_movie, "movieName": movieName})
    else:
        movies = os.path.join(settings.MEDIA_ROOT, "leadcopy", "movies.csv")
        df_r = pd.read_csv(movies, nrows=100)
        m = df_r.title.unique()
        return render(request, "users/collaborate.html", {"movies": m})


def user_content_based(request):
    if request.method == "POST":
        from .utility.Contetn_Based import start_content_Based
        movieName = request.POST.get('movie_name')
        result = start_content_Based(movieName)
        print("Results Content is ",result)
        movies = os.path.join(settings.MEDIA_ROOT, "leadcopy", "movies.csv")
        df_r = pd.read_csv(movies, nrows=100)
        m = df_r.title.unique()
        return render(request, "users/content_based.html",
                      {"movies": m, "results": result, "movieName": movieName})
    else:
        movies = os.path.join(settings.MEDIA_ROOT, "leadcopy", "movies.csv")
        df_r = pd.read_csv(movies, nrows=100)
        m = df_r.title.unique()
        return render(request, "users/content_based.html", {"movies": m})


