from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account, Transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from decimal import Decimal


@login_required
def dashboard(request):
    account, created = Account.objects.get_or_create(user=request.user)
    return render(request, 'atm/dashboard.html', {
        'account': account
    })

@login_required
def check_balance(request):
    return render(request, 'atm/check_balance.html', {
        'account': request.user.account
    })


@login_required
def deposit_view(request):
    account, _ = Account.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if amount > 0:
            account.deposit(amount)

            Transaction.objects.create(
                account=account,
                amount=amount,
                transaction_type='DEPOSIT'
            )

            messages.success(request, "Money deposited successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid amount.")

    return render(request, 'atm/deposit.html')

@login_required
def withdraw_view(request):
    account, _ = Account.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))

        if amount > 0:
            if account.withdraw(amount):

                Transaction.objects.create(
                    account=account,
                    amount=amount,
                    transaction_type='WITHDRAW'
                )

                messages.success(request, "Withdrawal successful!")
                return redirect('dashboard')
            else:
                messages.error(request, "Insufficient balance.")
        else:
            messages.error(request, "Invalid amount.")

    return render(request, 'atm/withdraw.html')

@login_required
def transactions_view(request):
    account, _ = Account.objects.get_or_create(user=request.user)

    transactions = Transaction.objects.filter(account=account).order_by('-timestamp')

    return render(request, 'atm/transactions.html', {
        'transactions': transactions
    })


def register_view(request):
    username = ''
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')


        if not username or not password or not confirm:
            messages.error(request, "All fields are required")
            return render(request, 'atm/register.html', {'username': username})

     
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return render(request, 'atm/register.html', {'username': username})

     
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'atm/register.html', {'username': username})


        user = User.objects.create_user(username=username, password=password)
        Account.objects.create(user=user)
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'atm/register.html', {'username': username})


def login_view(request):
    username = ''
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'atm/login.html', {'username': username})


def logout_view(request):
    logout(request)
    return redirect('login')
