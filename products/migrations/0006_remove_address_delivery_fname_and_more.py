# Generated manually to align the products schema with the current models.

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0005_address_delivery_fname_address_delivery_lname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='delivery_fname',
        ),
        migrations.RemoveField(
            model_name='address',
            name='delivery_lname',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipment_id',
        ),
        migrations.AddField(
            model_name='address',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_column='ORDER_CREATED_AT', default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='review',
            name='description',
            field=models.TextField(blank=True, db_column='REVIEW_DESCRIPTION', null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='image',
            field=models.ImageField(blank=True, db_column='REVIEW_IMAGE', null=True, upload_to='reviews/'),
        ),
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.ForeignKey(db_column='PRODUCT_ID', on_delete=django.db.models.deletion.CASCADE, to='products.artwork'),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(db_column='REVIEW_RATING'),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(db_column='USER_ID', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('shipment_id', models.AutoField(db_column='SHIPMENT_ID', primary_key=True, serialize=False)),
                ('shipment_date', models.DateField(blank=True, db_column='SHIPMENT_DATE', null=True)),
                ('shipment_company', models.CharField(blank=True, db_column='SHIPMENT_COMPANY', default='Bicol Express Courier', max_length=100, null=True)),
                ('shipment_status', models.CharField(db_column='SHIPMENT_STATUS', default='Pending', max_length=50)),
                ('address', models.ForeignKey(db_column='ADDRESS_ID', null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.address')),
            ],
            options={
                'db_table': 'shipment',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='shipment',
            field=models.OneToOneField(db_column='SHIPMENT_ID', null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.shipment'),
        ),
    ]
