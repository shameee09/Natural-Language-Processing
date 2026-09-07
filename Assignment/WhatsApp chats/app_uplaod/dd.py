#from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import *
import numpy as np
import pandas as pd
import time
import emoji
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,
                                UpdateView)
from . import models
from django.core.files.storage import FileSystemStorage
from app_uplaod.whatsapp import WhatsappFilrt
#import app_uplaod.whatsapp

# Create your views here.
class FileUploadView(View):
    form_class = WhatsAppForm
    success_url = reverse_lazy('success')
    template_name = 'create.html'
    failure_url= reverse_lazy('fail')
    filenot_url= reverse_lazy('filenot')
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    def post(self, request, *args, **kwargs):
        #print('inside post')
        form = self.form_class(request.POST, request.FILES)
        #print('inside form')
        txtfile=request.FILES['upload_file']
        fs=FileSystemStorage()
        name=fs.save(txtfile.name,txtfile)
        url=fs.url(name)
        #print(url)
        if txtfile.name.endswith('.txt'):
            #print("inside if")
            form.save()
            #print('inside save')
            try:
                df = pd.read_csv(url,header=None,error_bad_lines=False,encoding='utf8')
                #return df
            except FileNotFoundError:
                return HttpResponse('Please rename your text file without space in file name')
            obj=WhatsappFilrt()
            dataset=obj.PreProcessing(url)
            result,result1=obj.Wholeprocess(dataset)
            return render(request, "succ_msg.html", {'result': result,'result1' : result1})

        else:
            return redirect(self.failure_url)

class Success(TemplateView):
    template_name='succ_msg.html'

class Failure(TemplateView):
    template_name='fail.html'

class FileNotfound(TemplateView):
    tempalte_name='filenot.html'
class AboutUs(TemplateView):
    template_name='aboutus.html'



#class WhatsappAnalaysis(View):
