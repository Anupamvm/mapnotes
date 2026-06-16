from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("properties", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="distance_from_home_km",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name="property",
            name="drive_time_minutes",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
