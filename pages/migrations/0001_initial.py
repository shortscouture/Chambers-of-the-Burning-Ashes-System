

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
                ("full_name", models.CharField(max_length=45)),
                ("permanent_address", models.TextField(max_length=255)),
                ("landline_number", models.CharField(blank=True, max_length=15)),
                ("mobile_number", models.CharField(max_length=11)),
                (
                    "email_address",
                    models.EmailField(default="no-email@example.com", max_length=45),
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
                ("full_contribution", models.BooleanField()),
                ("six_month_installment", models.BooleanField()),
                ("official_receipt", models.IntegerField(blank=True, null=True)),
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
            name="ColumbaryRecord",
            fields=[
                (
                    "vault_id",
                    models.CharField(max_length=8, primary_key=True, serialize=False),
                ),
                ("section", models.CharField(max_length=7)),
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
