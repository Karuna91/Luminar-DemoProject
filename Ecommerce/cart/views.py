from django.shortcuts import render,redirect
from shop.models import Product
from .models import Cart,Payment,Order_table
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User


@login_required
def add_to_cart(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        if(p.stock>0):
            cart.quantity+=1
            cart.save()
            p.stock-=1
            p.save()

    except:
        if(p.stock):
            cart=Cart.objects.create(product=p,user=u,quantity=1)
            cart.save()
            p.stock-=1
            p.save()

    return redirect('cart:cart_views')

def cart_views(request):
    u = request.user
    cart = Cart.objects.filter(user=u)
    total = 0
    for i in cart:
        total = total + i.quantity * i.product.price
    return render(request, 'cart_views.html', {'cart': cart, 'total': total})
@login_required
def cart_decrement(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        if(cart.quantity>1):
            cart.quantity-=1
            cart.save()
            p.stock+=1
            p.save()
        else:
            cart.delete()
            p.stock+=1
            p.save()

    except:
        pass

    return cart_views(request)

@login_required
def delete(request,pk):
    p=Product.objects.get(id=pk)
    u=request.user
    try:
        cart=Cart.objects.get(user=u,product=p)
        cart.delete()
        p.stock+=cart.quantity
        p.save()

    except:
        pass

    return redirect('cart:cart_views')


def place_order(request):
    if(request.method=='POST'):
        ph = request.POST.get('phone')
        a = request.POST.get('address')
        pin = request.POST.get('pin')
        u = request.user
        c = Cart.objects.filter(user=u)
        total=0
        for i in c:
            total = total+(i.quantity*i.product.price)   #total amount of cart
        total = int(total*100)
        
        # create razor pay client using ourAPI  credentails
        client=razorpay.Client(auth=('rzp_test_p9aZcQz0WqsU3d','oCDywolA2RkSadTPmBtY3ZA2'))

        #create order in razorpay
        response_payment = client.order.create(dict(amount=total,currency="INR"))


        print(response_payment)
        order_id = response_payment['id']
        order_status = response_payment['status']
        if order_status=="created":
            p = Payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:
                o = Order_table.objects.create(user=u,product=i.product,order_id=order_id,address=a,phone=ph,pin=pin,no_of_items=i.quantity)
                o.save()
        response_payment['name']=u.username
        return render(request, 'payment.html',{'payment' : response_payment})

    return render(request,'place_order.html')


@csrf_exempt
def payment_status(request,u):
    print(request.user.is_authenticated)
    if not request.user.is_authenticated:
        u = User.objects.get(username = u)
        login(request,u)
        print(u.is_authenticated) #true


    if (request.method=="POST"):
        username = request.user
        response = request.POST #Razorpay response after payment
        # print(response)
        # print(u)
        param_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature' : response['razorpay_signature']

        }
        client = razorpay.Client(auth=('rzp_test_p9aZcQz0WqsU3d', 'oCDywolA2RkSadTPmBtY3ZA2'))

        try:
            status = client.utility.verify_payment_signature(param_dict)  #to check the authenticity of razorpay signature
            print(status)

            #After successful payment

            #Retrieve a payment record with particular order_id
            ord = Payment.objects.get(order_id=response['razorpay_order_id'])
            ord.razorpay_payment = response['razorpay_payment_id'] #Edits payment id response['razorpay_order_id']
            ord.paid = True #edit paid to True
            ord.save()
            # print(u)
            user = User.objects.get(username = u)
            print(user.email)
            c = Cart.objects.filter(user = user)

            #Filter the order_table details for particular user with order_id= response['razorpay_order_id']
            o = Order_table.objects.filter(user = user,order_id = response['razorpay_order_id'])
            print(o)
            for i in o:
                i.payment_status = "paid"
                i.save()
            c.delete()
            return render(request, 'payment_status.html',{'status':True})

        except:
            return render(request,'payment_status.html',{'status':False})

    return render(request, 'payment_status.html')


@login_required
def orderview(request):
    u = request.user
    customer = Order_table.objects.filter(user=u,payment_status="paid")
    return render(request,'orderview.html',{'customer' : customer,'u': u.username})