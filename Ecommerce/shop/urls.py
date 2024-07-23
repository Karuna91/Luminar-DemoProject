from django.urls import path
from shop import views
app_name='shop'
urlpatterns = [
    path('',views.home,name="home"),
    path('category',views.category,name='category'),
    path('product/<int:i>',views.product,name='product'),
    path('product_details/<int:i>',views.product_details,name="product_details"),
    path('register',views.register,name='register'),
    path('user_login',views.user_login,name='user_login'),
    path('user_logout',views.user_logout,name='user_logout'),
]
