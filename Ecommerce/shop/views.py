from django.shortcuts import render,redirect
from shop.models import Category,Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate ,login,logout
from django.contrib import messages
def home(request):
    return render(request,'home.html')

def category(request):
    c = Category.objects.all()
    return render(request,'category.html',{'c': c })

def product(request,i):
    c = Category.objects.get(id=i)
    p = Product.objects.filter(category=c)
    return render(request,'product.html',{'c' : c, 'p' : p })

def product_details(request,i):
    p = Product.objects.get(id=i)
    return render(request,'product_details.html',{'p': p})

def register(request):
    if (request.method == "POST"):
        u = request.POST['u']
        p = request.POST['p']
        c = request.POST['c']
        f = request.POST['f']
        l = request.POST['l']
        e = request.POST['e']
        if (c == p):
            s = User.objects.create_user(username=u, password=p, first_name=f, last_name=l,email=e)
            s.save()
            return redirect('shop:home')
    return render(request,'register.html')

def user_login(request):
    if (request.method == "POST"):
        u = request.POST['u']
        p = request.POST['p']
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            return redirect('shop:home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request,'login.html')

def user_logout(request):
    logout(request)
    return redirect('shop:user_login')