from rest_framework import serializers
from django.contrib.auth.models import User
# internal
from api.models import CodeExplainer
from api.utils import send_code_to_api

class CodeExplainSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExplainer
        fields = ["id", "input", "output"]
        extra_kwargs = {
            "output": {"read_only": True}, #bruh obviously
        }
    
    def create(self, validated_data):
        ce = CodeExplainer(**validated_data)
        output = send_code_to_api(validated_data["input"])
        ce.output = output
        ce.save()
        return ce

class UserSerializer(serializer.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs ={
            "password":("write_only":True)
        }
        