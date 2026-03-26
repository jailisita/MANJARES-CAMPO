from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.urls import reverse_lazy

class CustomLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin_dashboard')
        return reverse_lazy('catalog')

@login_required
def login_success(request):
    """
    Fallback redirect view.
    """
    if request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('catalog')

from .forms import UserProfileForm

@login_required
def profile_view(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            password_form = SetPasswordForm(request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, '¡Tu perfil ha sido actualizado con éxito!')
                return redirect('profile')
            else:
                messages.error(request, 'Por favor corrige los errores en tu perfil.')
        
        elif 'update_password' in request.POST:
            user_form = UserProfileForm(instance=request.user)
            password_form = SetPasswordForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, '¡Tu contraseña ha sido actualizada con éxito!')
                return redirect('profile')
            else:
                messages.error(request, 'Por favor corrige los errores en tu contraseña.')
    else:
        user_form = UserProfileForm(instance=request.user)
        password_form = SetPasswordForm(request.user)
    
    return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'password_form': password_form,
        'active_nav': 'profile'
    })
