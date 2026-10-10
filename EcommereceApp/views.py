from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from .models import *
from adminapp.models import *
from django.db.models import Q
import uuid
from django.core.mail import send_mail
from django.conf import settings
import random



def register(request):
    if request.method == "POST":
        n = request.POST.get('name')   
        em = request.POST.get('email')
        p = request.POST.get('phone')
        pw = request.POST.get('password')
        pwc = request.POST.get('confirm_password')
        if pw == pwc:
            if Register.objects.filter(email=em).exists():
                messages.error(request, "Email already Exist:")
                return redirect('registration')
            hash_password = make_password(pw)
            us=Register(name=n,email=em,phone=p,password=hash_password)
            us.save()
            return redirect('userlogin')
        else:
            messages.error(request, "Password and Confirm Password Are not Matched")
            return redirect('registration')
        
    return render(request,'registration.html')

def userlogin(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = Register.objects.filter(email=email).first()

        if user:

            if check_password(password, user.password):

                # Profile milega, nahi mila to automatically create hoga
                profile, created = UserProfile.objects.get_or_create(
                    user=user
                )

                request.session["user_id"] = user.id
                request.session["user_name"] = user.name
                request.session["user_email"] = user.email
                request.session["phone"] = user.phone

                if profile.profile_image:
                    request.session["image"] = profile.profile_image.url
                else:
                    request.session["image"] = ""

                messages.success(request, "Login Successfully")

                return redirect("ecommerce")

            else:

                messages.error(request, "Invalid Password")
                return redirect("userlogin")

        else:

            messages.error(request, "Email does not exist")
            return redirect("userlogin")

    return render(request, "userlogin.html")

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")

        try:

            user = Register.objects.get(
                email=email
            )

            # OTP generate
            otp = random.randint(100000, 999999)

            # Session me save
            request.session["reset_email"] = email
            request.session["reset_otp"] = str(otp)

            # Email send
            send_mail(
                "ShopMart - Password Reset OTP",

                f"""
        Hello {user.name},

        Your password reset OTP is:

        {otp}

        This OTP is valid for this password reset request.

        Regards,
        ShopMart
        """,

                None,

                [email],

                fail_silently=False
            )

            return redirect("verify_forgot_otp")

        except Register.DoesNotExist:

            messages.error(
                request,
                "Email address is not registered."
            )

    return render(
        request,
        "forgot_password.html"
    )

def verify_forgot_otp(request):

    if "reset_email" not in request.session:
        return redirect("forgot_password")

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        saved_otp = request.session.get("reset_otp")

        if entered_otp == saved_otp:

            # OTP correct
            request.session["otp_verified"] = True

            return redirect("reset_password")

        else:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

    return render(
        request,
        "verifiy_forgot_otp.html"
    )

def reset_password(request):

    # OTP verify hua hai ya nahi
    if not request.session.get("otp_verified"):
        return redirect("forgot_password")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(
                request,
                "reset_password.html",
                {
                    "error": "Passwords do not match"
                }
            )

        # YAHAN reset_email use hoga
        email = request.session.get("reset_email")

        if not email:
            return redirect("forgot_password")

        user = Register.objects.filter(
            email=email
        ).first()

        if not user:
            return redirect("forgot_password")

        from django.contrib.auth.hashers import make_password

        user.password = make_password(password)
        user.save()

        # Reset session clear
        request.session.pop("reset_email", None)
        request.session.pop("reset_otp", None)
        request.session.pop("otp_verified", None)

        # Password successfully reset
        return redirect("userlogin")

    return render(
        request,
        "reset_password.html"
    )

def userlogout(request):

    request.session.flush()

    messages.success(request, "Logout Successfully")

    return redirect("userlogin")

def ecommerce(request):

    products = Product.objects.filter(status=True)
    categories = Category.objects.filter(status=True)

    # Login check
    user_id = request.session.get("user_id")

    wishlist_products = []

    # Agar user login hai tabhi wishlist check karo
    if user_id:

        user = Register.objects.get(
            id=user_id
        )

        wishlist_products = Wishlist.objects.filter(
            user=user,
            is_active=True
        ).values_list(
            "product_id",
            flat=True
        )

    return render(request, "ecommerce.html", {
        "products": products,
        "categories": categories,
        "wishlist_products": wishlist_products
    })
def records(request):

    categories = Category.objects.filter(status=True)

    search = request.GET.get("search")

    if search:

        data = Product.objects.filter(
            Q(product_name__icontains=search) |
            Q(description__icontains=search) |
            Q(sub_category__Sub_category_name__icontains=search) |
            Q(category__category_name__icontains=search) |
            Q(brand__brand_name__icontains=search)
        ).filter(
            status=True
        )

    else:

        data = Product.objects.filter(
            status=True
        )

    return render(
        request,
        "ecommerce.html",
        {
            "products": data,
            "categories": categories
        }
    )
   


def add_profile(request):

    user = Register.objects.get(id=request.session["user_id"])

    if request.method == "POST":

        image = request.FILES.get("profile_image")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        bio = request.POST.get("bio")

        profile, created = UserProfile.objects.get_or_create(user=user)

        profile.full_name = user.name
        profile.gender = gender
        profile.dob = dob
        profile.bio = bio

        if image:
            profile.profile_image = image

        profile.save()

        if profile.profile_image:
            request.session['image'] = profile.profile_image.url
        else:
            request.session['image'] = None 
          
        return redirect("view_profile")
    else:
        messages.info(request, "please fill the form")  
        return render(request, "add_profile.html")


def view_profile(request):

    user = Register.objects.get(id=request.session["user_id"])
    profile = UserProfile.objects.filter(user=user).first()
    address = Address.objects.filter(user=user).first()

    print("profile page email",user.email)
    return render(request, "view_profile.html", {
        "user": user,
        "profile": profile,
        "address": address,
    })

def edit_profile(request):
    user = Register.objects.get(id=request.session["user_id"])
    profile = UserProfile.objects.get(user=user)

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        user.name = request.POST.get("full_name")
        user.email = email
        user.save()
        request.session["user_name"] = user.name
        request.session["user_email"] = user.email


        profile.gender = request.POST.get("gender")
        profile.dob = request.POST.get("dob") or None
        profile.bio = request.POST.get("bio")

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        return redirect("view_profile")

    return render(request, "edit_profile.html", {
        "profile": profile
    })

def add_address(request):

    user=Register.objects.get(id=request.session["user_id"])

    if request.method=="POST":

        full_name=request.POST.get("full_name")
        phone=request.POST.get("phone")
        line1=request.POST.get("address_line1")
        line2=request.POST.get("address_line2")
        city=request.POST.get("city")
        state=request.POST.get("state")
        pincode=request.POST.get("pincode")

        Address.objects.create(

            user=user,
            full_name=full_name,
            phone=phone,
            address_line1=line1,
            address_line2=line2,
            city=city,
            state=state,
            pincode=pincode

        )

        return redirect("view_address")

    return render(request,"add_address.html")


def view_address(request):

    address=Address.objects.filter(user_id=request.session["user_id"])

    return render(request,"view_address.html",{

        "address":address

    })

from django.shortcuts import get_object_or_404

def edit_address(request,id):

    address=get_object_or_404(Address,id=id)

    if request.method=="POST":

        address.full_name=request.POST.get("full_name")
        address.phone=request.POST.get("phone")
        address.address_line1=request.POST.get("address_line1")
        address.address_line2=request.POST.get("address_line2")
        address.city=request.POST.get("city")
        address.state=request.POST.get("state")
        address.pincode=request.POST.get("pincode")

        address.save()

        return redirect("view_address")

    return render(request,"edit_address.html",{

        "address":address

    })

def delete_address(request,id):

    address=Address.objects.get(id=id)

    address.delete()

    return redirect("view_address")


def profile(request):

    user = Register.objects.get(id=request.session["user_id"])

    profile = UserProfile.objects.filter(user=user).first()

    return render(request,"profile.html",{
        "user":user,
        "profile":profile
    })



def product_details(request, id):

    product = get_object_or_404(Product, id=id)

    return render(request, "product_details.html", {
        "product": product
    })


def categoriess(request):
    categories = Category.objects.filter(status=True)

    return render(request, "categories.html", {
        "categories": categories
    })



def products(request):
    products = Product.objects.filter(status=True)

    return render(request, "products.html", {
        "products": products
    })

def category_products(request, category_id):

    category = Category.objects.get(id=category_id)

    products = Product.objects.filter(
        category=category,
        status=True
    )

    categories = Category.objects.filter(
        status=True
    )

    return render(request, "ecommerce.html", {
        "products": products,
        "category": category,
        "categories": categories
    })

def cart(request):

    # Login required
    if "user_id" not in request.session:
        return redirect("userlogin")

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    cart = Cart.objects.filter(
        user=user,
        is_active=True
    ).first()

    cart_items = []
    total = 0

    if cart:

        cart_items = CartItem.objects.filter(
            cart=cart
        ).select_related("product")

        for item in cart_items:

            # Quantity ke according total
            item.total_price = (
                item.price * item.quantity
            )

            total += item.total_price

    return render(
        request,
        "cart.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "total": total
        }
    )


# -----------------------------------
# ADD TO CART
# -----------------------------------

def add_to_cart(request, id):

    # Login required
    if "user_id" not in request.session:
        return redirect("userlogin")

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    product = Product.objects.get(
        id=id
    )

    cart, created = Cart.objects.get_or_create(
        user=user,
        is_active=True
    )

    cart_item = CartItem.objects.filter(
        cart=cart,
        product=product
    ).first()

    if cart_item:

        # Same product already hai
        # to quantity increase hogi
        cart_item.quantity += 1

        cart_item.total_price = (
            cart_item.price *
            cart_item.quantity
        )

        cart_item.save()

    else:

        price = (
            product.discount_price
            if product.discount_price
            else product.price
        )

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=1,
            price=price,
            total_price=price
        )

    return redirect("cart")


# -----------------------------------
# INCREASE QUANTITY
# -----------------------------------

def increase_cart(request, id):

    if "user_id" not in request.session:
        return redirect("userlogin")

    item = CartItem.objects.get(
        id=id,
        cart__user_id=request.session["user_id"]
    )

    item.quantity += 1

    item.total_price = (
        item.price * item.quantity
    )

    item.save()

    return redirect("cart")


# -----------------------------------
# DECREASE QUANTITY
# -----------------------------------

def decrease_cart(request, id):

    if "user_id" not in request.session:
        return redirect("userlogin")

    item = CartItem.objects.get(
        id=id,
        cart__user_id=request.session["user_id"]
    )

    if item.quantity > 1:

        item.quantity -= 1

        item.total_price = (
            item.price * item.quantity
        )

        item.save()

    else:

        item.delete()

    return redirect("cart")


# -----------------------------------
# REMOVE CART ITEM
# -----------------------------------

def remove_cart(request, id):

    if "user_id" not in request.session:
        return redirect("userlogin")

    item = CartItem.objects.get(
        id=id,
        cart__user_id=request.session["user_id"]
    )

    item.delete()

    return redirect("cart")


def checkout(request):
    user = Register.objects.get(
        id=request.session["user_id"]
    )

    # =========================
    # USER ADDRESSES
    # =========================

    address = Address.objects.filter(
        user=user
    )


    # =========================
    # DIRECT BUY NOW
    # =========================

    buy_now_product_id = request.session.get(
        "buy_now_product"
    )

    if buy_now_product_id:

        product = Product.objects.get(
            id=buy_now_product_id
        )

        quantity = request.session.get(
            "buy_now_quantity",
            1
        )

        # Current product price
        if product.discount_price:
            price = product.discount_price
        else:
            price = product.price

        total_price = price * quantity

        # Template ko CartItem jaisa data dene ke liye
        cart_items = [{
            "product": product,
            "quantity": quantity,
            "price": price,
            "total_price": total_price
        }]

        total = total_price


    # =========================
    # NORMAL CART
    # =========================

    else:

        cart = Cart.objects.filter(
            user=user,
            is_active=True
        ).first()

        cart_items = []
        total = 0

        if cart:

            cart_items = CartItem.objects.filter(
                cart=cart
            ).select_related("product")

            for item in cart_items:

                # Current product price
                if item.product.discount_price:
                    item.price = item.product.discount_price
                else:
                    item.price = item.product.price

                item.total_price = (
                    item.price * item.quantity
                )

                total += item.total_price


    return render(
        request,
        "checkout.html",
        {
            "address": address,
            "cart_items": cart_items,
            "total": total,
        }
    )



def send_order_invoice_email(order, user):

    subject = f"ShopMart - Order Invoice #{order.order_number}"

    message = f"""
Hello {order.address.full_name},

Thank you for shopping with ShopMart!

Your order has been successfully placed.

================================
          ORDER INVOICE
================================

Order Number : {order.order_number}
Customer     : {order.address.full_name}
Phone        : {order.address.phone}

Address:
{order.address.address_line1}
{order.address.city} - {order.address.pincode}

--------------------------------
ORDER ITEMS
--------------------------------
"""

    # GET ORDER ITEMS
    for item in OrderItem.objects.filter(order=order):

        message += f"""
Product  : {item.product.product_name}
Quantity : {item.quantity}
Price    : ₹{item.product_price}
Total    : ₹{item.total_price}
"""

    message += f"""
--------------------------------

Subtotal       : ₹{order.subtotal}
Discount       : ₹{order.discount_amount}
Shipping       : ₹{order.shipping_charge}
Grand Total    : ₹{order.grand_total}

Payment Method : {order.payment_method}
Payment Status : {order.payment_status}
Order Status   : {order.order_status}

================================

Thank you for choosing ShopMart!

ShopMart Team
"""

    print("Sending email to:", user.email)

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )

    print("EMAIL SENT SUCCESSFULLY")
# =========================================================
# PLACE ORDER
# =========================================================
def place_order(request, address_id):

    # -----------------------------------------
    # PAYMENT DETAILS
    # -----------------------------------------

    payment_method = request.POST.get("payment_method")
    upi_id = request.POST.get("upi_id")
    card_number = request.POST.get("card_number")


    # -----------------------------------------
    # USER
    # -----------------------------------------

    user = Register.objects.get(
        id=request.session["user_id"]
    )


    # -----------------------------------------
    # ADDRESS
    # -----------------------------------------

    address = Address.objects.get(
        id=address_id,
        user=user
    )


    # -----------------------------------------
    # CHECK BUY NOW
    # -----------------------------------------

    buy_now_product_id = request.session.get(
        "buy_now_product"
    )

    buy_now_quantity = request.session.get(
        "buy_now_quantity",
        1
    )


    # -----------------------------------------
    # ORDER ITEMS DATA
    # -----------------------------------------

    order_items_data = []

    subtotal = 0


    # =========================================
    # DIRECT BUY NOW
    # =========================================

    if buy_now_product_id:

        product = Product.objects.get(
            id=buy_now_product_id
        )

        if product.stock <= 0:
            return redirect(
                "product_details",
                id=product.id
            )


        # Discounted price
        if product.discount_price:
            price = product.discount_price
        else:
            price = product.price


        total_price = price * buy_now_quantity


        order_items_data.append({
            "product": product,
            "price": price,
            "quantity": buy_now_quantity,
            "total_price": total_price
        })


        subtotal = total_price


    # =========================================
    # NORMAL CART
    # =========================================

    else:

        cart = Cart.objects.filter(
            user=user,
            is_active=True
        ).first()


        if not cart:
            return redirect("cart")


        cart_items = CartItem.objects.filter(
            cart=cart
        ).select_related("product")


        if not cart_items.exists():
            return redirect("cart")


        for item in cart_items:

            # Current product price
            if item.product.discount_price:
                item.price = item.product.discount_price
            else:
                item.price = item.product.price


            item.total_price = (
                item.price * item.quantity
            )


            subtotal += item.total_price


            order_items_data.append({
                "product": item.product,
                "price": item.price,
                "quantity": item.quantity,
                "total_price": item.total_price
            })


    # -----------------------------------------
    # DISCOUNT
    # -----------------------------------------

    discount_amount = 0


    # -----------------------------------------
    # SHIPPING
    # -----------------------------------------

    shipping_charge = 0


    # -----------------------------------------
    # GRAND TOTAL
    # -----------------------------------------

    grand_total = (
        subtotal
        - discount_amount
        + shipping_charge
    )


    # -----------------------------------------
    # ORDER NUMBER
    # -----------------------------------------

    order_number = "ORD" + str(
        uuid.uuid4().int
    )[:8]


    # -----------------------------------------
    # PAYMENT STATUS
    # -----------------------------------------

    payment_status = 'pending'

    if payment_method == 'COD':
        payment_status = 'pending'

    elif payment_method == 'UPI':
        payment_status = 'success'

    elif payment_method == 'CARD':
        payment_status = 'success'
        
    else:
        payment_status = 'pending'


    # -----------------------------------------
    # CREATE ORDER
    # -----------------------------------------

    order = Order.objects.create(

        order_number=order_number,

        user=user,

        address=address,

        subtotal=subtotal,

        discount_amount=discount_amount,

        shipping_charge=shipping_charge,

        grand_total=grand_total,

        payment_method=payment_method,

        payment_status=payment_status,

        order_status="Pending"
    )


    # -----------------------------------------
    # CREATE ORDER ITEMS
    # -----------------------------------------

    for item in order_items_data:

        OrderItem.objects.create(

            order=order,

            product=item["product"],

            product_price=item["price"],

            quantity=item["quantity"],

            total_price=item["total_price"]
        )


    Payment.objects.create(
        order=order,
        payment_method=payment_method,
        amount=grand_total,
        payment_status=payment_status
    )


    # -----------------------------------------
    # SEND INVOICE EMAIL
    # -----------------------------------------

    try:

        send_order_invoice_email(
            order,
            user
        )

        print("Invoice email sent successfully")

    except Exception as e:

        print("Invoice Email Error:", e)


    # =========================================
    # CLEAR BUY NOW SESSION
    # =========================================

    if buy_now_product_id:

        request.session.pop(
            "buy_now_product",
            None
        )

        request.session.pop(
            "buy_now_quantity",
            None
        )


    # =========================================
    # CLEAR NORMAL CART
    # =========================================

    else:

        cart_items.delete()

        cart.is_active = False
        cart.save()


    # -----------------------------------------
    # ORDER SUCCESS
    # -----------------------------------------

    return redirect(
        "order_success",
        order_id=order.id
    )


def order_success(request, order_id):

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    order = Order.objects.get(
        id=order_id,
        user=user
    )

    return render(request, "order_success.html", {
        "order": order
    })


def buy_now(request, id):

    # Login required
    if "user_id" not in request.session:
        return redirect("userlogin")

    product = Product.objects.get(id=id)

    # Out of stock
    if product.stock <= 0:
        return redirect(
            "product_details",
            id=id
        )

    # Direct Buy Now product
    request.session["buy_now_product"] = id
    request.session["buy_now_quantity"] = 1

    return redirect("checkout")


def order_details(request, order_id):

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    order = get_object_or_404(
        Order,
        id=order_id,
        user=user
    )

    order_items = OrderItem.objects.filter(
        order=order
    )

    payment = Payment.objects.filter(
        order=order
    ).first()

    return render(request, "order_details.html", {
        "order": order,
        "order_items": order_items,
        "payment": payment,
    })

def my_orders(request):

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    orders = Order.objects.filter(
        user=user
    ).order_by("-ordered_at")

    return render(
        request,
        "my_order.html",
        {
            "orders": orders
        }
    )
# -----------------------------------
# ADD / TOGGLE WISHLIST
# -----------------------------------

def add_wishlist(request, product_id):

    # Login required
    if "user_id" not in request.session:
        return redirect("userlogin")

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    product = Product.objects.get(
        id=product_id
    )

    wishlist = Wishlist.objects.filter(
        user=user,
        product=product
    ).first()

    if wishlist:

        if wishlist.is_active:

            # Already active → remove
            wishlist.is_active = False
            wishlist.save()

        else:

            # Previously removed → add again
            wishlist.is_active = True
            wishlist.save()

    else:

        # First time add
        Wishlist.objects.create(
            user=user,
            product=product,
            is_active=True
        )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "ecommerce"
        )
    )


# -----------------------------------
# WISHLIST PAGE
# -----------------------------------

def wishlist(request):

    # Login required
    if "user_id" not in request.session:
        return redirect("userlogin")

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    wishlist_items = Wishlist.objects.filter(
        user=user,
        is_active=True
    ).select_related("product")

    return render(
        request,
        "wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )


# -----------------------------------
# REMOVE WISHLIST
# -----------------------------------

def remove_wishlist(request, product_id):

    # Login required
    if "user_id" not in request.session:
        return redirect("userlogin")

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    Wishlist.objects.filter(
        user=user,
        product_id=product_id
    ).update(
        is_active=False
    )

    return redirect("wishlist")

def get_cart_count(request):

    cart = request.session.get("cart", {})

    return sum(cart.values())

from django.utils import timezone


def cancel_order(request, order_id):

    if "user_id" not in request.session:
        return redirect("userlogin")

    user = Register.objects.get(
        id=request.session["user_id"]
    )

    order = Order.objects.filter(
        id=order_id,
        user=user
    ).first()

    if not order:
        return redirect("my_orders")

    # Sirf Pending / Confirmed order cancel hoga
    if order.order_status not in ["Pending", "Confirmed"]:
        return redirect(
            "order_details",
            order_id=order.id
        )

    if request.method == "POST":

        cancel_reason = request.POST.get(
            "cancel_reason"
        )

        if not cancel_reason:
            return render(
                request,
                "cancel_order.html",
                {
                    "order": order,
                    "error": "Please select a cancellation reason."
                }
            )

        order.order_status = "Cancelled"
        order.cancel_reason = cancel_reason
        order.cancelled_at = timezone.now()

        if order.payment_status == "Paid":
            order.payment_status = "Refund Pending"

        order.save()

        return redirect(
            "order_details",
            order_id=order.id
        )

    return render(
        request,
        "cancel_order.html",
        {
            "order": order
        }
    )

def user_roles(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    users = Register.objects.all().order_by("-id")

    return render(request, "user_roles.html", {
        "users": users
    })


def update_user_role(request, user_id):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    user = Register.objects.get(id=user_id)

    if request.method == "POST":

        role = request.POST.get("role")

        user.role = role
        user.save()

    return redirect("user_roles")

def contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        messages.success(
            request,
            "Your message has been sent successfully."
        )

        return redirect("contact")

    return render(request, "contact.html")







           


