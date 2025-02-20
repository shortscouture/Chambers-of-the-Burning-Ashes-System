# Generated by Django 5.1.2 on 2025-02-20 05:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("account_id", models.AutoField(primary_key=True, serialize=False)),
                ("username", models.CharField(max_length=45, unique=True)),
                ("password", models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name="ChatQuery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_message", models.TextField()),
                ("bot_response", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("customer_id", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(default="Unknown", max_length=50)),
                ("middle_name", models.CharField(blank=True, max_length=50, null=True)),
                ("last_name", models.CharField(default="Unknown", max_length=50)),
                ("suffix", models.CharField(blank=True, max_length=10, null=True)),
                ("country", models.CharField(default="Philippines", max_length=100)),
                (
                    "address_line_1",
                    models.CharField(default="Unknown Address", max_length=255),
                ),
                (
                    "address_line_2",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("city", models.CharField(default="Unknown City", max_length=100)),
                (
                    "province_or_state",
                    models.CharField(default="Unknown Province", max_length=100),
                ),
                ("postal_code", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "landline_number",
                    models.CharField(blank=True, max_length=15, null=True),
                ),
                (
                    "mobile_number",
                    models.CharField(blank=True, max_length=11, null=True),
                ),
                (
                    "email_address",
                    models.EmailField(blank=True, max_length=45, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("declined", "Declined"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HolderOfPrivilege",
            fields=[
                (
                    "holder_of_privilege_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("full_name", models.CharField(max_length=45)),
                (
                    "email_address",
                    models.EmailField(blank=True, max_length=45, null=True),
                ),
                ("address", models.CharField(blank=True, max_length=45, null=True)),
                ("landline_number", models.IntegerField(blank=True, null=True)),
                ("mobile_number", models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("payment_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "mode_of_payment",
                    models.CharField(
                        choices=[
                            ("Full Payment", "Full Payment"),
                            ("6-Month Installment", "6-Month Installment"),
                        ],
                        default="Full Payment",
                        max_length=20,
                    ),
                ),
                ("Full_payment_receipt_1", models.IntegerField(blank=True, null=True)),
                ("six_month_receipt_1", models.IntegerField(blank=True, null=True)),
                ("six_month_receipt_2", models.IntegerField(blank=True, null=True)),
                ("six_month_receipt_3", models.IntegerField(blank=True, null=True)),
                ("six_month_receipt_4", models.IntegerField(blank=True, null=True)),
                ("six_month_receipt_5", models.IntegerField(blank=True, null=True)),
                ("six_month_receipt_6", models.IntegerField(blank=True, null=True)),
                (
                    "Full_payment_amount_1",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "six_month_amount_1",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "six_month_amount_2",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "six_month_amount_3",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "six_month_amount_4",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "six_month_amount_5",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "six_month_amount_6",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        editable=False,
                        max_digits=10,
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TwoFactorAuth",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=45)),
                ("otp", models.CharField(max_length=6)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_verified", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Beneficiary",
            fields=[
                ("beneficiary_id", models.AutoField(primary_key=True, serialize=False)),
                ("first_beneficiary_name", models.CharField(max_length=255)),
                (
                    "second_beneficiary_name",
                    models.CharField(blank=True, max_length=45, null=True),
                ),
                (
                    "third_beneficiary_name",
                    models.CharField(blank=True, max_length=45, null=True),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="beneficiaries",
                        to="pages.customer",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ColumbaryRecord",
            fields=[
                (
                    "vault_id",
                    models.CharField(max_length=8, primary_key=True, serialize=False),
                ),
                ("section", models.CharField(max_length=7)),
                ("level", models.CharField(max_length=1)),
                ("issuance_date", models.DateField(null=True)),
                ("expiration_date", models.DateField(null=True)),
                ("inurnment_date", models.DateField(blank=True, null=True)),
                (
                    "issuing_parish_priest",
                    models.CharField(blank=True, max_length=45, null=True),
                ),
                (
                    "urns_per_columbary",
                    models.CharField(
                        choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("Vacant", "Vacant"), ("Occupied", "Occupied")],
                        default="Vacant",
                        max_length=10,
                    ),
                ),
                (
                    "beneficiary",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pages.beneficiary",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pages.customer",
                    ),
                ),
                (
                    "holder_of_privilege",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pages.holderofprivilege",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ParishAdministrator",
            fields=[
                ("admin_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="pages.account"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ParishStaff",
            fields=[
                ("staff_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="pages.account"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InquiryRecord",
            fields=[
                (
                    "letter_of_intent_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                (
                    "columbary_vault",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pages.columbaryrecord",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pages.customer",
                    ),
                ),
                (
                    "parish_administrator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pages.parishadministrator",
                    ),
                ),
                (
                    "parish_staff",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pages.parishstaff",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="columbaryrecord",
            name="parish_staff",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="pages.parishstaff",
            ),
        ),
        migrations.AddField(
            model_name="columbaryrecord",
            name="payment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="pages.payment",
            ),
        ),
    ]

# Generated by Django 5.1.2 on 2025-02-19 05:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=45, unique=True)),
                ('password', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='ChatQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_message', models.TextField()),
                ('bot_response', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('suffix', models.CharField(blank=True, max_length=10, null=True)),
                ('country', models.CharField(default='Philippines', max_length=100)),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('province_or_state', models.CharField(max_length=100)),
                ('postal_code', models.CharField(blank=True, max_length=20, null=True)),
                ('landline_number', models.CharField(blank=True, max_length=15, null=True)),
                ('mobile_number', models.CharField(blank=True, max_length=13, null=True)),
                ('email_address', models.EmailField(blank=True, max_length=45, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('declined', 'Declined')], default='pending', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='HolderOfPrivilege',
            fields=[
                ('holder_of_privilege_id', models.AutoField(primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=45)),
                ('email_address', models.EmailField(blank=True, max_length=45, null=True)),
                ('address', models.CharField(blank=True, max_length=45, null=True)),
                ('landline_number', models.IntegerField(blank=True, null=True)),
                ('mobile_number', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TwoFactorAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=45)),
                ('otp', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Beneficiary',
            fields=[
                ('beneficiary_id', models.AutoField(primary_key=True, serialize=False)),
                ('first_beneficiary_name', models.CharField(max_length=255)),
                ('second_beneficiary_name', models.CharField(blank=True, max_length=45, null=True)),
                ('third_beneficiary_name', models.CharField(blank=True, max_length=45, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='beneficiaries', to='pages.customer')),
            ],
        ),
        migrations.CreateModel(
            name='ColumbaryRecord',
            fields=[
                ('vault_id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('section', models.CharField(max_length=7)),
                ('issuance_date', models.DateField(null=True)),
                ('expiration_date', models.DateField(null=True)),
                ('inurnment_date', models.DateField(blank=True, null=True)),
                ('issuing_parish_priest', models.CharField(blank=True, max_length=45, null=True)),
                ('urns_per_columbary', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], max_length=1, null=True)),
                ('beneficiary', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.beneficiary')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.customer')),
                ('holder_of_privilege', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.holderofprivilege')),
            ],
        ),
        migrations.CreateModel(
            name='ParishAdministrator',
            fields=[
                ('admin_id', models.AutoField(primary_key=True, serialize=False)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pages.account')),
            ],
        ),
        migrations.CreateModel(
            name='ParishStaff',
            fields=[
                ('staff_id', models.AutoField(primary_key=True, serialize=False)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pages.account')),
            ],
        ),
        migrations.CreateModel(
            name='InquiryRecord',
            fields=[
                ('letter_of_intent_id', models.AutoField(primary_key=True, serialize=False)),
                ('columbary_vault', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.columbaryrecord')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.customer')),
                ('parish_administrator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.parishadministrator')),
                ('parish_staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.parishstaff')),
            ],
        ),
        migrations.AddField(
            model_name='columbaryrecord',
            name='parish_staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.parishstaff'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('mode_of_payment', models.CharField(choices=[('Full Payment', 'Full Payment'), ('6-Month Installment', '6-Month Installment')], default='Full Payment', max_length=20)),
                ('Full_payment_receipt_1', models.IntegerField(blank=True, null=True)),
                ('six_month_receipt_1', models.IntegerField(blank=True, null=True)),
                ('six_month_receipt_2', models.IntegerField(blank=True, null=True)),
                ('six_month_receipt_3', models.IntegerField(blank=True, null=True)),
                ('six_month_receipt_4', models.IntegerField(blank=True, null=True)),
                ('six_month_receipt_5', models.IntegerField(blank=True, null=True)),
                ('six_month_receipt_6', models.IntegerField(blank=True, null=True)),
                ('Full_payment_amount_1', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('six_month_amount_1', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('six_month_amount_2', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('six_month_amount_3', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('six_month_amount_4', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('six_month_amount_5', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('six_month_amount_6', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=10, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='pages.customer')),
            ],
        ),
        migrations.AddField(
            model_name='columbaryrecord',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pages.payment'),
        ),
    ]
