from bson import ObjectId
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from main.forms import RequestForm, LoginForm, SignUpForm, AttachmentForm
from main.models import User, Request, Attachment


def create_request_view(request, request_id=None):
    if request_id:
        request_instance = get_object_or_404(Request, pk=request_id)
    else:
        request_instance = None

    if request.method == 'POST':
        # Bind the forms to POST data
        form = RequestForm(request.POST, instance=request_instance)
        attachment_form = AttachmentForm(request.POST, request.FILES)
        files = request.FILES.getlist('file')  # Handle multiple files

        if form.is_valid():
            # Save the request
            new_request = form.save()

            # Save attachments
            for file in files:
                Attachment.objects.create(request=new_request, file=file)

            if request_id:
                messages.success(request, "Request updated successfully!")
            else:
                messages.success(request, "Request created successfully!")
            return redirect('main_page')
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        # For GET requests, populate the forms
        form = RequestForm(instance=request_instance)
        attachment_form = AttachmentForm()

    return render(request, 'main/create_request.html', {
        'form': form,
        'attachment_form': attachment_form,
        'is_edit': bool(request_instance),
        'request_id': request_id,
        'request_instance': request_instance
    })


def delete_request_view(request, request_id):
    if not request.session.get('is_admin', False):
        messages.error(request, "You do not have permission to delete requests.")
        return redirect('main_page')

    request_instance = get_object_or_404(Request, pk=request_id)
    request_instance.delete()
    messages.success(request, "Request deleted successfully!")
    return redirect('main_page')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                print(user)
                print(type(user))
                if check_password(password, user.password):  # Ensure passwords match
                    request.session['user_id'] = str(user._id)
                    request.session['is_admin'] = user.is_admin
                    return redirect('main_page')
                else:
                    form.add_error('password', 'Invalid password')
            except User.DoesNotExist:
                form.add_error('email', 'User with this email does not exist')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})


def main_page_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    try:
        user = User.objects.get(_id=ObjectId(user_id))
        if user.is_admin:
            print(user._id)
            requests = Request.objects.filter(admin_user=user)
        else:
            requests = Request.objects.filter(client_user=user)

        # print(requests[0].status)
        return render(
            request,
            'main/main_page.html',
            {'user': user, 'requests': requests}
        )
    except User.DoesNotExist:
        return redirect('login')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        user_type = request.POST.get('user_type')  # Get user type from form data
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            alternate_phone_number = form.cleaned_data['alternate_phone_number']
            password = make_password(form.cleaned_data['password'])
            user_type = form.cleaned_data['user_type']
            full_name = form.cleaned_data.get('full_name') if user_type == 'client' else None
            national_id = form.cleaned_data.get('national_id') if user_type == 'client' else None
            address = form.cleaned_data.get('address') if user_type == 'client' else None

            # Create the user
            user = User.objects.create(
                username=username,
                email=email,
                phone_number=phone_number,
                alternate_phone_number=alternate_phone_number,
                password=password,
                is_admin=(user_type == 'admin'),
                full_name=full_name,
                national_id=national_id,
                address=address,
            )
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, f'main/signup_{form.data.get("user_type", "client")}.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
