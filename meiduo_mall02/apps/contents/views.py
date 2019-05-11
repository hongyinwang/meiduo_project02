from django.shortcuts import redirect, render

# Create your views here.
from django.urls import reverse
from django.views import View


class Index(View):
    def get(self,request):

        return render(request,'index.html')

