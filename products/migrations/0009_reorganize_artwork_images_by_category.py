import os
import shutil

from django.conf import settings
from django.db import migrations
from django.utils.text import slugify


def reorganize_artwork_images(apps, schema_editor):
    Artwork = apps.get_model('products', 'Artwork')

    for artwork in Artwork.objects.select_related('category').exclude(image='').exclude(image__isnull=True):
        current_path = str(artwork.image)
        current_name = os.path.basename(current_path)
        if not current_name:
            continue

        category_name = ''
        if artwork.category_id and artwork.category:
            category_name = artwork.category.category_name or ''

        category_slug = slugify(category_name) or 'uncategorized'
        target_rel_dir = os.path.join('artwork_pics', category_slug).replace('\\', '/')
        target_rel_path = f'{target_rel_dir}/{current_name}'

        if current_path == target_rel_path:
            continue

        source_abs_path = os.path.join(settings.MEDIA_ROOT, current_path)
        if not os.path.exists(source_abs_path):
            legacy_source = os.path.join(settings.MEDIA_ROOT, 'artwork_pics', current_name)
            if os.path.exists(legacy_source):
                source_abs_path = legacy_source
            else:
                continue

        target_abs_dir = os.path.join(settings.MEDIA_ROOT, target_rel_dir)
        os.makedirs(target_abs_dir, exist_ok=True)

        stem, ext = os.path.splitext(current_name)
        candidate_name = current_name
        candidate_rel_path = target_rel_path
        candidate_abs_path = os.path.join(settings.MEDIA_ROOT, candidate_rel_path)
        counter = 1

        while os.path.exists(candidate_abs_path) and os.path.normcase(candidate_abs_path) != os.path.normcase(source_abs_path):
            candidate_name = f'{stem}-{artwork.prod_id}-{counter}{ext}'
            candidate_rel_path = f'{target_rel_dir}/{candidate_name}'
            candidate_abs_path = os.path.join(settings.MEDIA_ROOT, candidate_rel_path)
            counter += 1

        if os.path.normcase(source_abs_path) != os.path.normcase(candidate_abs_path):
            shutil.move(source_abs_path, candidate_abs_path)

        artwork.image = candidate_rel_path
        artwork.save(update_fields=['image'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_alter_artwork_image'),
    ]

    operations = [
        migrations.RunPython(reorganize_artwork_images, migrations.RunPython.noop),
    ]
