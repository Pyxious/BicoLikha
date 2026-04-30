from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_artiststockadjustmentrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopularAd',
            fields=[
                ('ad_id', models.AutoField(db_column='AD_ID', primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, db_column='AD_TITLE', max_length=255, null=True)),
                ('image', models.ImageField(db_column='AD_IMAGE', upload_to='popular_ads/')),
                ('is_active', models.BooleanField(db_column='IS_ACTIVE', default=True)),
                ('display_order', models.PositiveIntegerField(db_column='DISPLAY_ORDER', default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='CREATED_AT')),
            ],
            options={
                'db_table': 'popular_ads',
                'ordering': ['display_order', '-created_at'],
            },
        ),
    ]
