from django.test import TestCase
from models import ColumbaryRecord

ColumbaryRecord.objects.filter(section="W-1", level="A")

# Create your tests here.
