from django.db import models

# Create your models here.

class CodeExplainer(models.Model):
    input: models.TextField(unique=True) #user prompt
    output: models.TextField(blank=True, null=True) #chatgpt response
    
    class Meta:
        db_table = "code_explainer"
