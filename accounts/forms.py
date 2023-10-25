from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(min_length=8, max_length=15, 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm password', 
            'class': 'form-control'
        })
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'city', 'country', 'password']
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Enter password', 
        })
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(f"Passwords don't match! <br> {1} <br> {2}".format(password, confirm_password))
