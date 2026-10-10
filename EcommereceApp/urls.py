from django.urls import path
from EcommereceApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns =[
    path('register/',views.register,name='registeration'),
    path('userlogin/',views.userlogin,name='userlogin'),
    path("forgot-password/",views.forgot_password,name="forgot_password"),
    path("verify-forgot-otp/",views.verify_forgot_otp,name="verify_forgot_otp"),
    path("reset-password/",views.reset_password,name="reset_password"),
    path('ecommerce/',views.ecommerce,name='ecommerce'),
    path('userlogout/',views.userlogout,name='userlogout'),

    path('profile/',views.profile,name='profile'),
    path("add_profile/", views.add_profile, name="add_profile"),
    path('view_profile/', views.view_profile, name='view_profile'),
    path("edit_profile//", views.edit_profile, name="edit_profile"),

    path("add_address/", views.add_address, name="add_address"),
    path("view-address/", views.view_address, name="view_address"),
    path("edit-address/<int:id>/", views.edit_address, name="edit_address"),
    path("delete-address/<int:id>/", views.delete_address, name="delete_address"),
    path("product/<int:id>/", views.product_details, name="product_details"),
    path("categories/", views.categoriess, name="categories"),
    path("category/<int:category_id>/",views.category_products,name="category_products"),
    path("products/", views.products, name="products"),
    path("add-to-cart/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("remove-cart/<int:id>/", views.remove_cart, name="remove_cart"),
    path('records',views.records,name='records'),
    path("increase-cart/<int:id>/", views.increase_cart, name="increase_cart"),
    path("decrease-cart/<int:id>/", views.decrease_cart, name="decrease_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("place-order/<int:address_id>/",views.place_order,name='place_order'),
    path("order-success/<int:order_id>/",views.order_success,name='order_success'),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("order-details/<int:order_id>/",views.order_details,name="order_details"),
    path("wishlist/",views.wishlist,name="wishlist"),

    path("wishlist/add/<int:product_id>/",views.add_wishlist,name="add_wishlist"),
    path("wishlist/remove/<int:product_id>/",views.remove_wishlist,name="remove_wishlist"),
    path("buy-now/<int:id>/",views.buy_now,name="buy_now"),
    path("cancel-order/<int:order_id>/",views.cancel_order,name="cancel_order"),
    path("contact/",views.contact,name="contact"),

    


]











if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root = settings.MEDIA_ROOT
    )