from django.db import models
from adminapp.models import *
from django.utils import timezone


class Register(models.Model):
        name = models.CharField(max_length=100)
        email = models.EmailField(unique=True)
        phone = models.CharField(max_length=15)
        password = models.CharField(max_length=300)
        created_at = models.DateTimeField(auto_now_add=True)
        is_active = models.BooleanField(default=True)
        role = models.CharField(max_length=20,default="Customer")

        def __str__(self):
              return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(Register,on_delete=models.CASCADE,related_name="profile")
    profile_image = models.ImageField(upload_to="profile/",blank=True,null=True)
    gender = models.CharField( max_length=10,blank=True,null=True)
    dob = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name        
    

class Address(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    is_default = models.BooleanField(default=False)




class Cart(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.user.name

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name


class Order(models.Model):

    order_number = models.CharField(max_length=50, unique=True)

    user = models.ForeignKey(
        Register,
        on_delete=models.CASCADE
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50,
        default="COD"
    )

    payment_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    order_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    ordered_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    cancel_reason = models.CharField(
    max_length=200,
    blank=True,
    null=True
)

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    cancelled_by = models.CharField(
    max_length=20,
    blank=True,
    null=True
)

    def __str__(self):
        return self.order_number



class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.product.product_name




class Payment(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    payment_method = models.CharField(
        max_length=50
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    failure_reason = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.order.order_number)


class Order_Track(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        'Register',
        on_delete=models.CASCADE
    )

    address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True
    )

    order_number = models.CharField(
        max_length=50,
        unique=True
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    shipping_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=50
    )

    payment_status = models.CharField(
        max_length=20,
        default="Pending"
    )

    order_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    ordered_at = models.DateTimeField(
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


class Wishlist(models.Model):

    user = models.ForeignKey(
        Register,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.user.name + " - " + self.product.product_name

    

class Contact(models.Model):

    name = models.CharField(max_length=100)

    email = models.EmailField()

    subject = models.CharField(max_length=200)

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_replied = models.BooleanField(default=False)

    reply = models.TextField(blank=True, null=True)

    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.subject 
   


    
        


    


    

