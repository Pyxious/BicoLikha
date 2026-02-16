from django.db import models

# 1. Matches your 'categories' table exactly
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

# 2. Matches your 'artist' table
class Artist(models.Model):
    artist_id = models.AutoField(primary_key=True)
    artist_name = models.CharField(max_length=150)
    artist_description = models.TextField(blank=True, null=True)
    artist_municipality = models.CharField(max_length=100)

    class Meta:
        db_table = 'artist'

    def __str__(self):
        return self.artist_name


class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    stock_quantity = models.IntegerField(default=0)
    stock_status = models.CharField(max_length=50, default='In Stock')

    class Meta:
        db_table = 'stock' # Matches your SQL table name

    def __str__(self):
        return f"Stock ID: {self.stock_id} ({self.stock_quantity})"

# 3. Matches your 'product' table
# products/models.py

class Artwork(models.Model):
    prod_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, db_column='prod_name')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='prod_price')
    description = models.TextField(db_column='prod_description', blank=True, null=True)
    image = models.ImageField(upload_to='artwork_pics/', db_column='prod_image_path', null=True, blank=True)
    
    # Foreign Keys
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    artist_ref = models.ForeignKey(Artist, on_delete=models.CASCADE, db_column='artist_id')
    
    # ADD OR CHECK THIS LINE:
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, db_column='stock_id')
    
    # In your SQL, there is a user_id for the admin who added it
    user_id = models.IntegerField(default=1) 

    class Meta:
        db_table = 'product'

        # Add this to products/models.py

class CustomUser(models.Model):
    # Use IntegerField so we can force it to match your Django Login ID
    user_id = models.IntegerField(primary_key=True) 
    user_role = models.CharField(max_length=1, default='A')
    user_lname = models.CharField(max_length=100)
    user_fname = models.CharField(max_length=100)
    user_email = models.EmailField(max_length=150)
    user_password_hash = models.CharField(max_length=255, default='django_managed')

    class Meta:
        db_table = 'users'

class AdminProfile(models.Model):
    # This must match the user_id above
    user_id = models.IntegerField(primary_key=True)
    admin_access = models.CharField(max_length=45, default='Full Access')

    class Meta:
        db_table = 'admin'