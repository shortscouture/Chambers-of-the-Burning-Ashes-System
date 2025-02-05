from django.shortcuts import render
from rest_framework import views, status
from rest_framework.response import Response


# internals
from api.serializers import CodeExplainSerializer
from api.models import CodeExplainer
# Create your views here.
class CodeExplainView(views.APIView):
    serializer_class = CodeExplainSerializer
    
    def get(self,request,format=None):
        qs = CodeExplainer.objects.all()
        serializer = self.serializer_class(qs, many=True)
        return Response(serializer.data)
    
    def post(self,request,format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView:
    pass

class TokenView:
    pass