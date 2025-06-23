from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PaymentProof, MegaVideo

class CustomUserCreationForm(UserCreationForm):
    payment_proof = forms.ImageField(
        required=True,
        help_text='Upload proof of payment (JPG, JPEG, PNG, max 2MB)',
        widget=forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png'})
    )
    
    agree_to_terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Conditions',
        error_messages={'required': 'You must agree to the Terms and Conditions to register.'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Simplify password help text
        self.fields['password1'].help_text = 'Create a secure password.'
        # Remove password2 help text completely
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            payment_proof = PaymentProof(
                user=user,
                image=self.cleaned_data['payment_proof']
            )
            payment_proof.save()
        return user

class MegaVideoForm(forms.ModelForm):
    class Meta:
        model = MegaVideo
        fields = ['title', 'description', 'mega_file_link', 'thumbnail', 'thumbnail_url', 'membership_tier', 'is_free']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png',
                'data-preview': '#thumbnail-preview'
            }),
            'thumbnail_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Or enter a URL to an image'
            })
        }
        help_texts = {
            'thumbnail': 'Upload a thumbnail image (max 2MB, JPG/PNG)',
            'thumbnail_url': 'Alternatively, you can provide a URL to an existing image',
            'mega_file_link': 'Enter the MEGA link for the video',
            'membership_tier': 'Select the membership tier required to access this video',
            'is_free': 'Make this video available to all users regardless of membership'
        }

    def clean(self):
        cleaned_data = super().clean()
        thumbnail = cleaned_data.get('thumbnail')
        thumbnail_url = cleaned_data.get('thumbnail_url')

        if not thumbnail and not thumbnail_url:
            raise forms.ValidationError(
                "Please either upload a thumbnail image or provide a thumbnail URL"
            )

        return cleaned_data
