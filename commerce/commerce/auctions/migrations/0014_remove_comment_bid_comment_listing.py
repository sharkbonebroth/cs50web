# Generated by Django 4.0.3 on 2022-03-17 04:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_auctionlisting_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='bid',
        ),
        migrations.AddField(
            model_name='comment',
            name='listing',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='auctions.auctionlisting'),
            preserve_default=False,
        ),
    ]