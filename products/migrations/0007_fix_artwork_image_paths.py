from django.db import migrations


def prefix_artwork_image_paths(apps, schema_editor):
    Artwork = apps.get_model('products', 'Artwork')

    for artwork in Artwork.objects.exclude(image='').exclude(image__isnull=True):
        image_name = str(artwork.image)
        if image_name.startswith('artwork_pics/'):
            continue

        artwork.image = f'artwork_pics/{image_name}'
        artwork.save(update_fields=['image'])


def unprefix_artwork_image_paths(apps, schema_editor):
    Artwork = apps.get_model('products', 'Artwork')

    for artwork in Artwork.objects.exclude(image='').exclude(image__isnull=True):
        image_name = str(artwork.image)
        if not image_name.startswith('artwork_pics/'):
            continue

        artwork.image = image_name[len('artwork_pics/'):]
        artwork.save(update_fields=['image'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_address_delivery_fname_and_more'),
    ]

    operations = [
        migrations.RunPython(prefix_artwork_image_paths, unprefix_artwork_image_paths),
    ]
