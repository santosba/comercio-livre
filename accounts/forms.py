from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
      
    class Meta:
        model = CustomUser
        fields = ('username','email', 'first_name', 'last_name', 'password1', 'password2')


        labels = {
            'username':'Nome do Utilizador',
            'email': 'Email ',
            'first_name': 'Nome',
            'last_name': 'Apelido',
            'password1': 'Palavra-passe',
            'password2': 'Confirme a Palavra-passe',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


        self.fields['username'].widget.attrs.update({
            'placeholder':'maximo 10 caracteres',
            'maxlength':'10'
        })
        
    
        self.fields['password1'].label = 'Palavra-passe'
        self.fields['password1'].widget.attrs['placeholder'] = 'palavra-passe'
        self.fields['password2'].label = 'Confirme a Palavra-passe'
        self.fields['password2'].widget.attrs['placeholder'] = 'confirme a palavra-passe'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        username= cleaned_data.get("username")
        if CustomUser.objects.filter(email=email).exists():
            self.add_error("email", "Email já existe.")
        if CustomUser.objects.filter(username=username).exists():
            self.add_error("username", "Nome de utilizador já está em uso.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email','morada', 'telefone')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
