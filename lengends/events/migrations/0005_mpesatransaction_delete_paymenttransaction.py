# Generated by Django 5.1.1 on 2024-12-08 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_paymenttransaction_phone_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MpesaTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_request_id', models.CharField(blank=True, max_length=255, null=True)),
                ('checkout_request_id', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('result_code', models.IntegerField(blank=True, null=True)),
                ('result_desc', models.TextField(blank=True, null=True)),
                ('mpesa_receipt_number', models.CharField(blank=True, max_length=255, null=True)),
                ('transaction_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Success', 'Success'), ('Failed', 'Failed')], default='Failed', max_length=10)),
                ('callback_url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='PaymentTransaction',
        ),
    ]