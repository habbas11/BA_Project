from bson import ObjectId
from django.core.exceptions import ValidationError
from django import forms
from main.models import Request, User, Attachment


class RequestForm(forms.ModelForm):
    admin_user = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Admin User"
    )
    client_user = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Client User"
    )
    request_type = forms.ChoiceField(
        choices=[('new', 'New Request'), ('complaint', 'Complaint')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[
            ('open', 'Open'),
            ('under_processing', 'Under Processing'),
            ('closed', 'Closed')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label="Description"
    )

    class Meta:
        model = Request
        fields = ['admin_user', 'client_user', 'request_type', 'status', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            all_users = User.objects.values('_id', 'username', 'is_admin')  # Fetch all users
            admin_choices = []
            client_choices = []

            # Categorize users into admin and client
            for user in all_users:
                if user['is_admin']:
                    admin_choices.append((str(user['_id']), user['username']))
                else:
                    client_choices.append((str(user['_id']), user['username']))

            self.fields['admin_user'].choices = admin_choices
            self.fields['client_user'].choices = client_choices
        except Exception as e:
            print(f"Error initializing form: {e}")
            self.fields['admin_user'].choices = []
            self.fields['client_user'].choices = []

    def clean_admin_user(self):
        admin_user_id = self.cleaned_data['admin_user']

        try:
            # Convert to ObjectId
            user_id_obj = ObjectId(admin_user_id)

            # Retrieve the user
            admin_user = User.objects.get(_id=user_id_obj)

            # Check if the user is an admin
            if not admin_user.is_admin:
                raise ValidationError("The selected user is not an admin.")

            return admin_user
        except User.DoesNotExist:
            raise ValidationError("The selected admin user does not exist.")
        except Exception as e:
            raise ValidationError(f"Error validating admin user: {e}")

    def clean_client_user(self):
        client_user_id = self.cleaned_data['client_user']

        try:
            # Convert to ObjectId
            user_id_obj = ObjectId(client_user_id)

            # Retrieve the user
            client_user = User.objects.get(_id=user_id_obj)

            # Ensure the user is not an admin
            if client_user.is_admin:
                raise ValidationError("The selected user cannot be an admin.")

            return client_user
        except User.DoesNotExist:
            raise ValidationError("The selected client user does not exist.")
        except Exception as e:
            raise ValidationError(f"Error validating client user: {e}")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.admin_user = self.cleaned_data['admin_user']
        instance.client_user = self.cleaned_data['client_user']
        if commit:
            instance.save()
        return instance


class AttachmentForm(forms.ModelForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label="Attachments",
        required=False
    )

    class Meta:
        model = Attachment
        fields = ['file']


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    alternate_phone_number = forms.CharField(max_length=15, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[('admin', 'Admin'), ('client', 'Client')])
    full_name = forms.CharField(max_length=255, required=False)
    national_id = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=500, required=False)

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        if user_type == 'client':
            if not cleaned_data.get('full_name'):
                self.add_error('full_name', 'Full name is required for clients.')
            if not cleaned_data.get('national_id'):
                self.add_error('national_id', 'National ID is required for clients.')
            if not cleaned_data.get('address'):
                self.add_error('address', 'Address is required for clients.')
        return cleaned_data
