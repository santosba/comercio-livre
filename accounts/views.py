from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, FormView, RedirectView, TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, UserUpdateForm
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests


# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('login')

    def get(self, request):
        form = self.form_class()
        context = {'RegisteredForm': form}
        return render(request,self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario Criado com Sucesso !')
            return redirect(self.success_url)
        else:
            context = {'RegisteredForm': form}
            return render(request, self.template_name, context)

class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def  get(self, request):

        form = self.form_class()
        context = {'LoginForm': form}
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
        context = {'LoginForm': form}
        return render(request, self.template_name, context)





class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')
    
    @method_decorator(csrf_exempt)  # Exempt CSRF for GET requests
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            if request.user.is_authenticated:
                logout(request)
                messages.info(request, 'You have successfully logged out.')
            return redirect(self.next_page)
        return super().dispatch(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    login_url = reverse_lazy('login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('profile')
    login_url = reverse_lazy('login')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

class UserListView(LoginRequiredMixin, TemplateView):
    """Example of a view that requires admin permissions"""
    template_name = 'accounts/user_list.html'
    login_url = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to view this page.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context


