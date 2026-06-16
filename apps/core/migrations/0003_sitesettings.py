from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_project_is_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_address', models.CharField(
                    default='Castle Royale Magnifique, A19, Tower 1, 23rd floor, near Joshi gate, Bopodi, Pune 411020, India',
                    help_text='Used as origin for travel distance calculations on properties.',
                    max_length=500,
                )),
            ],
            options={
                'verbose_name': 'Site Settings',
                'verbose_name_plural': 'Site Settings',
            },
        ),
    ]
