from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from adminapp.models import AdminSignup,Category
from django.contrib import messages
import random
from django.utils import timezone
from EcommereceApp.models import Order,Contact


from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import check_password

from .models import *
from django.db.models import Q
from django.core.paginator import Paginator

from django.http import JsonResponse
from EcommereceApp.models import Register 

# Create your views here.

def signup(request):
    if request.method == "POST":
        im = request.FILES.get('image')
        n = request.POST.get('fullname')   
        em = request.POST.get('email')
        p = request.POST.get('phone')
        pw = request.POST.get('password')
        pwc = request.POST.get('confirm_password')
        if pw == pwc:
            if AdminSignup.objects.filter(email=em).exists():
                messages.error(request, "Email already Exist:")
                return redirect('signup')
            hash_password = make_password(pw)
            us=AdminSignup(image=im,name=n,email=em,phone=p,password=hash_password)
            us.save()
            return redirect('adminlogin')
        else:
            messages.error(request, "Password and Confirm Password Are not Matched")
            return redirect('signup')
        
    return render(request,'signup.html')

def adminlogin(request):

    if "admin_id" in request.session:
        return redirect("dashboard")

    if request.method == "POST":

        email = request.POST.get("username")
        password = request.POST.get("password")

        user = AdminSignup.objects.filter(email=email).first()

        if user is None:
            messages.error(request, "Email not registered")
            return redirect("adminlogin")

        if not check_password(password, user.password):
            messages.error(request, "Wrong Password")
            return redirect("adminlogin")

        otp = random.randint(100000, 999999)

        request.session["otp"] = str(otp)
        request.session["temp_email"] = email

        send_mail(
            "Login OTP",
            f"Your OTP is {otp}",
            "yourgmail@gmail.com",
            [email],
            fail_silently=False,
        )

        return redirect("verify_otp")

    return render(request, "adminlogin.html")


def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        if entered_otp == request.session.get("otp"):

            user = AdminSignup.objects.get(
                email=request.session["temp_email"]
            )

            request.session["admin_id"] = user.id
            request.session.modified = True

            del request.session["otp"]
            del request.session["temp_email"]

            return redirect("dashboard")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "verify_otp.html")

def forgot_admin_password(request):

    if request.method == "POST":

        email = request.POST.get("email")

        try:

            user = AdminSignup.objects.get(
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
        Hello Admin {user.name},

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

            return redirect("verify_admin_forgot")

        except AdminSignup.DoesNotExist:

            messages.error(
                request,
                "Email address is not registered."
            )

    return render(
        request,
        "forgot_admin_password.html"
    )

def verify_admin_forgot(request):

    if "reset_email" not in request.session:
        return redirect("forgot_admin_password")

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        saved_otp = request.session.get("reset_otp")

        if entered_otp == saved_otp:

            # OTP correct
            request.session["otp_verified"] = True

            return redirect("reset_admin_password")

        else:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

    return render(
        request,
        "verify_admin_password.html"
    )

def reset_admin_password(request):

    # OTP verify hua hai ya nahi
    if not request.session.get("otp_verified"):
        return redirect("forgot_admin_password")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(
                request,
                "reset_admin_password.html",
                {
                    "error": "Passwords do not match"
                }
            )

        # YAHAN reset_email use hoga
        email = request.session.get("reset_email")

        if not email:
            return redirect("forgot_admin_password")

        user = AdminSignup.objects.filter(
            email=email
        ).first()

        if not user:
            return redirect("forgot_admin_password")

        from django.contrib.auth.hashers import make_password

        user.password = make_password(password)
        user.save()

        # Reset session clear
        request.session.pop("reset_email", None)
        request.session.pop("reset_otp", None)
        request.session.pop("otp_verified", None)

        # Password successfully reset
        return redirect("adminlogin")

    return render(
        request,
        "reset_admin_password.html"
    )


def admin_profile(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    admin = AdminSignup.objects.get(
        id=request.session["admin_id"]
    )

    return render(request, "admin_profile.html", {
        "admin": admin
    })

def edit_admin_profile(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    admin = AdminSignup.objects.get(
        id=request.session["admin_id"]
    )

    if request.method == "POST":

        admin.name = request.POST.get("name")
        admin.email = request.POST.get("email")
        admin.phone = request.POST.get("phone")

        # Image optional hai
        if request.FILES.get("image"):
            admin.image = request.FILES.get("image")

        admin.save()

        return redirect("admin_profile")

    return render(request, "edit_admin_profile.html", {
        "admin": admin
    })
from django.contrib.auth.hashers import check_password, make_password


def change_admin_password(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    admin = AdminSignup.objects.get(
        id=request.session["admin_id"]
    )

    if request.method == "POST":

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Current password check
        if not check_password(
            current_password,
            admin.password
        ):
            return render(
                request,
                "change_password.html",
                {
                    "admin": admin,
                    "error": "Current password is incorrect."
                }
            )

        # New password match
        if new_password != confirm_password:
            return render(
                request,
                "change_password.html",
                {
                    "admin": admin,
                    "error": "New passwords do not match."
                }
            )

        # New password save
        admin.password = make_password(
            new_password
        )

        admin.save()

        return redirect("admin_profile")

    return render(
        request,
        "change_password.html",
        {
            "admin": admin
        }
    )



def dashboard(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")
    
    admin = AdminSignup.objects.get(
        id=request.session["admin_id"]
    )


    return render(request, "dashboard.html", {"admin": admin})

def users(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    users = Register.objects.all().order_by("-id")

    return render(request, "users.html", {
        "users": users,
        "users_count": users.count()
    })


def adminlogout(request):


    request.session.flush()

    return redirect("adminlogin")


def add_Category(request):
    if request.method =="POST":
        cn = request.POST.get('category_name')
        sl = request.POST.get('slug')
        im = request.FILES.get('image')
        desc = request.POST.get('description')
        st = request.POST.get('status')
        adc = Category(category_name=cn,slug=sl,image=im,description=desc,status=st)
        adc.save()
        messages.success(request, "Category Added Succesfully")
    return render(request,'category.html')



def add_subcategory(request):
    categories = Category.objects.all()
    if request.method == "POST":
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)

        name = request.POST.get('Sub_category_name')
        slug = request.POST.get('sub_slug')
        desc = request.POST.get('sub_desc')
        status = request.POST.get('status')

        ad = Add_sub_category(
            category=category,
            Sub_category_name=name,
            sub_slug=slug,
            sub_desc=desc,
            status=status
        )
        ad.save()

        return redirect('add_subcategory')

    return render(request, 'add_sub_category.html', {'categories': categories})


def View_Category(request):

    search = request.GET.get("search")

    if search:
        category = Category.objects.filter(
            category_name__icontains=search
        )
    else:
        category = Category.objects.all()

    return render(request, 'view_category.html', {'category': category})



def ViewSubCategory(request):

    search = request.GET.get("search")

    if search:
        sub_category = Add_sub_category.objects.filter(
            Q(Sub_category_name__icontains=search) |
            Q(category__category_name__icontains=search)
        )
    else:
        sub_category = Add_sub_category.objects.all()

    return render(request, 'view_sub_category.html', {
        'sub_category': sub_category
    })





def Edit_Category(request, id):
    category = Category.objects.get(id=id)

    if request.method == "POST":

        category.category_name = request.POST.get('category_name')
        category.slug = request.POST.get('slug')
        category.description = request.POST.get('description')
        category.status = request.POST.get("status") == "True"

        if request.FILES.get("image"):
            category.image = request.FILES.get("image")

        category.save()

        return redirect('view_category')

    return render(request, 'edit_category.html', {'edit_category': category})
    

def Delete_Category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect('view_category')


def Multiple_Delete_Category(request):
    if request.method == "POST":
        ids = request.POST.getlist("ids")
        Category.objects.filter(id__in=ids).delete()
    return redirect('view_category')


def Delete_All_Category(request):
    Category.objects.all().delete()
    return redirect('view_category')



def EditSubCategory(request, id):
    subcategory = Add_sub_category.objects.get(id=id)
    categories = Category.objects.all()

    if request.method == "POST":
        subcategory.category = Category.objects.get(id=request.POST.get("category"))
        subcategory.Sub_category_name = request.POST.get("subcategory")
        subcategory.sub_slug = request.POST.get("slug")
        subcategory.sub_desc = request.POST.get("description")
        subcategory.status = request.POST.get("status") == "True"
        subcategory.save()
        return redirect("sub_category_view")

    return render(request, "editSubcategory.html", {
        "subcategory": subcategory,
        "categories": categories,
    })

def DeleteSubCategory(request, id):

    subcategory = Add_sub_category.objects.get(id=id)

    subcategory.delete()

    return redirect("sub_category_view")

def Multiple_Delete_SubCategory(request):

    if request.method == "POST":

        ids = request.POST.getlist("ids")

        Add_sub_category.objects.filter(id__in=ids).delete()

    return redirect("sub_category_view")


def Delete_All_SubCategory(request):

    Add_sub_category.objects.all().delete()

    return redirect("sub_category_view")


def Add_Brand(request):

    if request.method == "POST":

        name = request.POST.get("brand_name")
        slug = request.POST.get("slug")
        image = request.FILES.get("image")
        description = request.POST.get("description")
        status = request.POST.get("status")

        # Multiple sub categories
        sub_category_ids = request.POST.getlist("sub_category")

        brand = Brand.objects.create(
            brand_name=name,
            slug=slug,
            image=image,
            description=description,
            status=True if status == "True" else False
        )

        # Multiple sub categories assign
        brand.sub_categories.set(sub_category_ids)

        return redirect("view_brand")

    sub_category = Add_sub_category.objects.all()

    return render(request, "brands.html", {
        "sub_category": sub_category
    })



def View_Brand(request):
    
    search = request.GET.get("search")

    if search:
        brand = Brand.objects.filter(
            brand_name__icontains=search
        )
    else:
        brand = Brand.objects.all()

    return render(request, "view_brand.html", {
        "brand": brand
    })

def load_brand(request):

    sub_category_id = request.GET.get("sub_category_id")


    brands = Brand.objects.filter(
        sub_categories__id=sub_category_id
    )


    data = []

    for brand in brands:
        data.append({
            "id": brand.id,
            "name": brand.brand_name
        })


    return JsonResponse(data, safe=False)


def Edit_Brand(request, id):

    brand = Brand.objects.get(id=id)

    if request.method == "POST":

        brand.brand_name = request.POST.get("brand_name")
        brand.slug = request.POST.get("slug")
        brand.description = request.POST.get("description")
        brand.status = request.POST.get("status")

        if request.FILES.get("image"):
            brand.image = request.FILES.get("image")

        brand.save()

        return redirect("view_brand")

    return render(request, "edit_brand.html", {"brand": brand})

def Delete_Brand(request, id):

    brand = Brand.objects.get(id=id)

    brand.delete()

    return redirect("view_brand")

def Multiple_Delete_Brand(request):

    if request.method == "POST":

        ids = request.POST.getlist("ids")

        Brand.objects.filter(id__in=ids).delete()

    return redirect("view_brand")

def Delete_All_Brand(request):

    Brand.objects.all().delete()

    return redirect("view_brand")


from .models import Category, Add_sub_category, Brand, Product



def Add_Product(request):

    if request.method == "POST":

        category = Category.objects.get(id=request.POST.get("category"))
        print(category.id)
        sub_category = Add_sub_category.objects.get(id=request.POST.get("sub_category"))
        brand = Brand.objects.get(id=request.POST.get("brand"))

        product_name = request.POST.get("product_name")
        slug = request.POST.get("slug")
        description = request.POST.get("description")
        price = request.POST.get("price")
        discount_price = request.POST.get("discount_price")
        stock = request.POST.get("stock")
        rating = request.POST.get("rating")
        status = request.POST.get("status")
        image = request.FILES.get("image")

        Product.objects.create(
            category=category,
            sub_category=sub_category,
            brand=brand,
            product_name=product_name,
            slug=slug,
            description=description,
            price=price,
            discount_price=discount_price,
            stock=stock,
            rating=rating,
            status=status,
            image=image
        )

        return redirect("view_product")

    category = Category.objects.all()
    sub_category = Add_sub_category.objects.all()
    brand = Brand.objects.all()

    
    return render(request, "add_product.html",{
        "category": category,
        "sub_category": sub_category,
        "brand": brand,
    })


def View_Product(request):
    
    search = request.GET.get("search")

    if search:
        product = Product.objects.filter(
            product_name__icontains=search
        )
    else:
        product = Product.objects.all()
    paginator = Paginator(product, 5)   # 5 products per page

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    return render(request, "view_product.html", {
        "page_obj": page_obj
    })
        

def Edit_Product(request, id):

    product = Product.objects.get(id=id)

    if request.method == "POST":

        product.category = Category.objects.get(id=request.POST.get("category"))
        product.sub_category = Add_sub_category.objects.get(id=request.POST.get("sub_category"))
        product.brand = Brand.objects.get(id=request.POST.get("brand"))

        product.product_name = request.POST.get("product_name")
        product.slug = request.POST.get("slug")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.discount_price = request.POST.get("discount_price")
        product.stock = request.POST.get("stock")
        product.rating = request.POST.get("rating")
        product.status = request.POST.get("status") == "True"

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        return redirect("view_product")

    return render(request, "edit_product.html", {
        "product": product,
        "category": Category.objects.all(),
        "sub_category": Add_sub_category.objects.filter(category=product.category),
        "brand": Brand.objects.filter(sub_category=product.sub_category),
    })

def Delete_Product(request, id):

    product = Product.objects.get(id=id)

    product.delete()

    return redirect("view_product")


def Multiple_Delete_Product(request):

    if request.method == "POST":

        ids = request.POST.getlist("ids")

        Product.objects.filter(id__in=ids).delete()

    return redirect("view_product")

def Delete_All_Product(request):

    Product.objects.all().delete()

    return redirect("view_product")


def load_subcategory(request):
    category_id = request.GET.get("category_id")

    subcategory = Add_sub_category.objects.filter(category_id=category_id)

    data = []
    for i in subcategory:
        data.append({
            "id": i.id,
            "name": i.Sub_category_name
        })

    return JsonResponse(data, safe=False)




def admin_orders(request):

    orders = Order.objects.all().order_by("-ordered_at")

    return render(request, "admin_orders.html", {
        "orders": orders
    })


def update_order_status(request, order_id):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    order = Order.objects.get(
        id=order_id
    )

    if request.method == "POST":

        status = request.POST.get(
            "order_status"
        )

        # Agar Admin Cancel select kare
        if status == "Cancelled":

            return redirect(
                "admin_cancel_order",
                order_id=order.id
            )

        # Normal status update
        order.order_status = status
        order.save()

    return redirect("admin_orders")

from django.utils import timezone


def admin_cancel_order(request, order_id):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    order = Order.objects.get(
        id=order_id
    )

    if request.method == "POST":

        reason = request.POST.get(
            "cancel_reason"
        )

        if not reason:
            return render(
                request,
                "admin_cancel_order.html",
                {
                    "order": order,
                    "error": "Please select a cancellation reason."
                }
            )

        order.order_status = "Cancelled"
        order.cancel_reason = reason
        order.cancelled_by = "Admin"
        order.cancelled_at = timezone.now()

        if order.payment_status == "Paid":
            order.payment_status = "Refund Pending"

        order.save()

        return redirect("admin_orders")

    return render(
        request,
        "admin_cancel_order.html",
        {
            "order": order
        }
    )

def block_unblock_users(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    users = Register.objects.all().order_by("-id")

    return render(request, "block_unblock_users.html", {
        "users": users
    })

def toggle_user_status(request, user_id):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    user = Register.objects.get(id=user_id)

    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True

    user.save()

    return redirect("block_unblock_users")

def delete_user(request, user_id):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    user = Register.objects.get(id=user_id)

    user.delete()

    return redirect("delete_users")

def delete_users(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    users = Register.objects.all().order_by("-id")

    return render(request, "delete_users.html", {
        "users": users
    })

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

def view_messages(request):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    contacts = Contact.objects.all().order_by("-created_at")

    return render(request, "view_messages.html", {
        "contacts": contacts
    })

def reply_message(request, id):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    contact = get_object_or_404(Contact, id=id)

    if request.method == "POST":

        reply = request.POST.get("reply")

        # Save reply in database
        contact.reply = reply
        contact.is_replied = True
        contact.replied_at = timezone.now()
        contact.save()

        # Send reply to user's email
        send_mail(
            subject=f"Reply from ShopMart - {contact.subject}",

            message=f"""
Hello {contact.name},

Thank you for contacting ShopMart.

Here is the reply to your message:

--------------------------------
{reply}
--------------------------------

Regards,
ShopMart Team
""",

            from_email=None,

            recipient_list=[
                contact.email
            ],

            fail_silently=False
        )

        return redirect("view_messages")

    return render(request, "reply_message.html", {
        "contact": contact
    })


def delete_message(request, id):

    if not request.session.get("admin_id"):
        return redirect("adminlogin")

    contact = Contact.objects.get(id=id)

    contact.delete()

    return redirect("view_messages")











    

    






