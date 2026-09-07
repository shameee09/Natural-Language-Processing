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
import matplotlib.pyplot as ax
#import matplotlib.pyplot as ax2
#import matplotlib.pyplot as ax3
##import matplotlib.pyplot as ax4
#import matplotlib.pyplot as ax5
from app_uplaod.whatsapp import WhatsappFilrt
import datetime
import seaborn as sns
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
            date_chart,media_count,msg_deleted_count,voice_call_count,video_call_count,stats, stats1=obj.statsWhatsApp(dataset)
            ax.rcParams.update({'figure.figsize':(9,7), 'figure.dpi':100})

            if(len(date_chart)>=2):
                ax1=sns.barplot(date_chart.index,date_chart["Date"])
                ax1.set_xticklabels(ax1.get_xticklabels(), rotation=40, ha="right")
                ax1.figure.savefig("date_chart.png")

            #if(len(media_count)>=2):
                #ax2=sns.barplot(media_count.index,media_count["Name"])
                #ax2.set_xticklabels(ax2.get_xticklabels(), rotation=40, ha="right")
                #ax2.figure.savefig("media_count.png")

            #if(len(msg_deleted_count)>=2):
                #ax3=sns.barplot(msg_deleted_count.index,msg_deleted_count["Name"])
                #ax3.set_xticklabels(ax3.get_xticklabels(), rotation=40, ha="right")
                #ax3.figure.savefig("msg_deleted_count.png")
            #if(len(voice_call_count)>=2):
                #ax4=sns.barplot(voice_call_count.index,voice_call_count["Name"])
                #ax3.set_xticklabels(ax3.get_xticklabels(), rotation=40, ha="right")
                #ax4.figure.savefig("voice_call_count.png")
            #if(len(video_call_count)>=2):
                #ax5=sns.barplot(video_call_count.index,video_call_count["Name"])
                #ax3.set_xticklabels(ax3.get_xticklabels(), rotation=40, ha="right")
                #ax5.figure.savefig("video_call_count.png")




            return render(request, "succ_msg.html", {'result': result,'result1' : result1,'stats':stats,'stats1':stats1,'media_count':media_count,'msg_deleted_count':msg_deleted_count,
                                                        'voice_call_count':voice_call_count,'video_call_count':video_call_count})

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
