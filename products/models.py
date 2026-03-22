from django.db import models
from django.contrib.auth.models import User

# --- 1. BASE TABLES ---
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    class Meta: db_table = 'categories'
    def __str__(self): return self.category_name

class Artist(models.Model):
    # Primary Key
    artist_id = models.AutoField(primary_key=True)
    
    # These MUST match your SQL column names exactly
    artist_name = models.CharField(max_length=150)
    artist_contact_num = models.CharField(max_length=20, null=True, blank=True)
    artist_description = models.TextField(null=True, blank=True)
    artist_municipality = models.CharField(max_length=100)
    artist_brgy = models.CharField(max_length=100)
    artist_zipcode = models.CharField(max_length=10)

    class Meta:
        db_table = 'artist' # Connects to your existing MySQL table

    def __str__(self):
        return self.artist_name

class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    stock_quantity = models.IntegerField(default=1)
    stock_status = models.CharField(max_length=50, default='In Stock')
    class Meta: db_table = 'stock'
    def __str__(self): return f"Stock {self.stock_id}"

# --- 2. USER & PROFILE TABLES ---
class CustomUser(models.Model):
    user_id = models.IntegerField(primary_key=True) 
    user_role = models.CharField(max_length=1, default='C')
    user_lname = models.CharField(max_length=100)
    user_fname = models.CharField(max_length=100)
    user_email = models.EmailField(max_length=150)
    user_contact_num = models.CharField(max_length=15, unique=True, null=True, blank=True)
    # ADD THIS LINE:
    profile_pix = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    user_password_hash = models.CharField(max_length=255, default='managed_by_django')

    class Meta:
        db_table = 'users'

# products/models.py

class CustomerProfile(models.Model):
    user_id = models.IntegerField(primary_key=True)
    cust_contact_num = models.CharField(max_length=20, default='09000000000')
    cust_st_name = models.CharField(max_length=255, default='', blank=True)
    cust_brngy = models.CharField(max_length=100, default='')
    cust_municipality = models.CharField(max_length=100, default='')
    cust_zipcode = models.CharField(max_length=10, default='')
    # NEW FIELDS: For Precise Map Delivery
    cust_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    cust_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = 'customer'

class AdminProfile(models.Model):
    user_id = models.IntegerField(primary_key=True)
    admin_access = models.CharField(max_length=45, default='Full Access')

    class Meta:
        db_table = 'admin'

    def __str__(self):
        return f"Admin {self.user_id}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)

# --- 3. CORE E-COMMERCE TABLES ---
class Timeline(models.Model):
    timeline_id = models.AutoField(primary_key=True)
    order_time = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'timeline'

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, db_column='user_id')
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE, db_column='timeline_id')
    order_total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_total_quantity = models.IntegerField(default=0)
    order_status = models.CharField(max_length=20, default='Pending')
    order_delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    class Meta: db_table = 'order'

class Artwork(models.Model):
    prod_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, db_column='prod_name')
    description = models.TextField(db_column='prod_description', blank=True, null=True) # Field is named 'description'
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='prod_price')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    artist_ref = models.ForeignKey(Artist, on_delete=models.CASCADE, db_column='artist_id')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_column='stock_id')
    user_id = models.IntegerField(default=2) 
    image = models.ImageField(upload_to='artwork_pics/', db_column='prod_image_path', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: db_table = 'product'
    def __str__(self): return self.title

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    product = models.ForeignKey(Artwork, on_delete=models.CASCADE, db_column='prod_id')
    op_quantity = models.IntegerField(db_column='op_quantity', default=1)
    op_subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='op_subtotal_amount')
    
    # NEW FIELD: This controls if the item is included in the current checkout
    is_selected = models.BooleanField(default=True) 

    class Meta:
        db_table = 'op_cart'

    def save(self, *args, **kwargs):
        # Data Integrity: Recalculate subtotal on every save
        self.op_subtotal_amount = self.product.price * self.op_quantity
        super().save(*args, **kwargs)

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    # This links the payment to your order
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order_id')
    payment_method = models.CharField(max_length=50)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    payment_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment' # Matches your SQL table


# Add this to products/models.py (usually near the top with other models)

class AuditLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    action = models.TextField()
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'