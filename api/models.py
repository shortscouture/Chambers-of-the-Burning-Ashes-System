from django.db import models

# Create your models here.

class CodeExplainer(models.Model):
    _input: models.TextField() #user prompt
    _output: models.TextField() #chatgpt response
    
    class Meta:
        db_table = "code_explainer"
