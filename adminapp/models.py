from django.db import models
# Create your models here.


class AdminSignup(models.Model):
    image = models.ImageField(upload_to='photo/')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=300)


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    image = models.ImageField(upload_to='category/')
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_name
    
class Add_sub_category(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    Sub_category_name=models.CharField(max_length=100)
    sub_slug = models.SlugField(max_length=150 , unique=True)
    sub_desc = models.TextField(blank=True , null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Sub_category_name



class Brand(models.Model):

    

    brand_name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    image = models.ImageField(upload_to="brand/")
    description = models.TextField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    sub_categories = models.ManyToManyField(
        Add_sub_category,
        blank=True
    )

    def __str__(self):
        return self.brand_name

    
    

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(Add_sub_category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    product_name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.IntegerField(default=0)

    image = models.ImageField(upload_to="product/")

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00
    )

    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    









