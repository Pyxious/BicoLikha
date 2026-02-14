from django.db import models

from django.db import models

# 1. Matches your 'categories' table
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'categories'  # Points to your SQL table name
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

# 3. Matches your 'product' table (Bridging your old 'Artwork' logic)
class Artwork(models.Model):
    # Using 'prod_id' as primary key to match your SQL
    prod_id = models.AutoField(primary_key=True)
    
    # Mapping to your SQL columns
    title = models.CharField(max_length=150, db_column='prod_name')
    description = models.TextField(db_column='prod_description', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='prod_price')
    
    # Relationship fields from your SQL
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    artist_ref = models.ForeignKey(Artist, on_delete=models.CASCADE, db_column='artist_id')
    
    # Handling the image
    image = models.ImageField(upload_to='artwork_pics/', db_column='prod_image_path', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True) # Django internal tracking

    class Meta:
        db_table = 'product' # Connects this model to your 'product' table

    def __str__(self):
        return f"{self.title} by {self.artist_ref.artist_name}"