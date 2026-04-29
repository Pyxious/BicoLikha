# Generated manually to add admin-reviewed artist stock adjustments.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_artistapplication_supplyinventory_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistStockAdjustmentRequest',
            fields=[
                ('request_id', models.AutoField(db_column='REQUEST_ID', primary_key=True, serialize=False)),
                ('adjustment_type', models.CharField(db_column='ADJUSTMENT_TYPE', max_length=20)),
                ('quantity', models.IntegerField(db_column='QUANTITY')),
                ('status', models.CharField(db_column='REQUEST_STATUS', default='Pending', max_length=50)),
                ('date_submitted', models.DateTimeField(auto_now_add=True, db_column='DATE_SUBMITTED')),
                ('date_reviewed', models.DateTimeField(blank=True, db_column='DATE_REVIEWED', null=True)),
                ('artist', models.ForeignKey(db_column='ARTIST_ID', on_delete=django.db.models.deletion.CASCADE, to='products.artist')),
                ('product', models.ForeignKey(db_column='PROD_ID', on_delete=django.db.models.deletion.CASCADE, to='products.artwork')),
            ],
            options={
                'db_table': 'artist_stock_adjustment_requests',
            },
        ),
    ]
