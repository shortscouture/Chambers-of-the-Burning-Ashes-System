from django.test import TestCase
from models import ColumbaryRecord
record = ColumbaryRecord(vault_id="E-1-A")
record.save()
print(record.status)
# Create your tests here.
