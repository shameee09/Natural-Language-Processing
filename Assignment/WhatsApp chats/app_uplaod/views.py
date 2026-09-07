from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView
from django.core.files.storage import FileSystemStorage

from .forms import *
from . import models

import numpy as np
import pandas as pd
import time
import emoji
import datetime
import matplotlib.pyplot as ax
import seaborn as sns

from app_uplaod.whatsapp import WhatsappFilrt


# ============================================================
# FILE UPLOAD VIEW
# ============================================================

class FileUploadView(View):

    form_class = WhatsAppForm
    template_name = 'create.html'

    success_url = reverse_lazy('success')
    failure_url = reverse_lazy('fail')
    filenot_url = reverse_lazy('filenot')

    # --------------------------------------------------------
    # GET
    # --------------------------------------------------------

    def get(self, request, *args, **kwargs):

        form = self.form_class()

        return render(
            request,
            self.template_name,
            {
                'form': form
            }
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    def post(self, request, *args, **kwargs):

        form = self.form_class(
            request.POST,
            request.FILES
        )

        # ----------------------------------------------------
        # Check whether file was uploaded
        # ----------------------------------------------------

        if 'upload_file' not in request.FILES:

            return redirect(self.filenot_url)

        txtfile = request.FILES['upload_file']

        # ----------------------------------------------------
        # Check file extension
        # ----------------------------------------------------

        if not txtfile.name.lower().endswith('.txt'):

            return redirect(self.failure_url)

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        fs = FileSystemStorage()

        name = fs.save(
            txtfile.name,
            txtfile
        )

        # IMPORTANT:
        # URL is for browser
        # PATH is for Python/Pandas

        file_url = fs.url(name)

        file_path = fs.path(name)

        print("Uploaded file URL:")
        print(file_url)

        print("Uploaded file path:")
        print(file_path)

        # ----------------------------------------------------
        # Check file exists
        # ----------------------------------------------------

        if not fs.exists(name):

            return HttpResponse(
                "Uploaded file could not be found."
            )

        # ----------------------------------------------------
        # Validate form
        # ----------------------------------------------------

        if form.is_valid():

            form.save()

        # ----------------------------------------------------
        # Test reading uploaded file
        # ----------------------------------------------------

        try:

            df = pd.read_csv(
                file_path,
                header=None,
                on_bad_lines='skip',
                encoding='utf-8'
            )

            print("File successfully read!")
            print("Rows:", len(df))
            print("Columns:", len(df.columns))

        except FileNotFoundError:

            return HttpResponse(
                "Uploaded file could not be found."
            )

        except UnicodeDecodeError:

            return HttpResponse(
                "Unable to read the file. Please make sure the WhatsApp chat file is UTF-8 encoded."
            )

        except Exception as e:

            return HttpResponse(
                f"Error while reading file: {str(e)}"
            )

        # ----------------------------------------------------
        # WhatsApp processing
        # ----------------------------------------------------

        try:

            obj = WhatsappFilrt()

            # IMPORTANT:
            # Pass the actual filesystem path,
            # not /media/... URL

            dataset = obj.PreProcessing(file_path)

            # ------------------------------------------------
            # Whole Process
            # ------------------------------------------------

            result, result1 = obj.Wholeprocess(dataset)

            # ------------------------------------------------
            # WhatsApp Statistics
            # ------------------------------------------------

            (
                date_chart,
                media_count,
                msg_deleted_count,
                voice_call_count,
                video_call_count,
                stats,
                stats1
            ) = obj.statsWhatsApp(dataset)

            # ------------------------------------------------
            # Date Chart
            # ------------------------------------------------

            ax.clf()

            if len(date_chart) >= 2:

                ax1 = sns.barplot(
                    x=date_chart.index,
                    y=date_chart["Date"]
                )

                ax1.set_xticklabels(
                    ax1.get_xticklabels(),
                    rotation=40,
                    ha="right"
                )

                ax1.set(
                    xlabel='Date',
                    ylabel='Message Count'
                )

                ax1.figure.savefig(
                    "static/output_image/date_charts.png",
                    bbox_inches='tight'
                )

                ax.clf()

            # ------------------------------------------------
            # Sentiment Analysis
            # ------------------------------------------------

            posneg = obj.sentimentalAnalysis(dataset)

            # ------------------------------------------------
            # Topic Modelling
            # ------------------------------------------------

            topic_modelling, dataset_topic = obj.topicModelling(
                dataset
            )

            # ------------------------------------------------
            # Save processed dataset
            # ------------------------------------------------

            dataset_topic.to_csv(
                "processed.csv",
                index=False
            )

            # ------------------------------------------------
            # Word Cloud
            # ------------------------------------------------

            wordclouds = obj.wordcloud(dataset)

            # ------------------------------------------------
            # SUCCESS PAGE
            # ------------------------------------------------

            return render(
                request,
                "succ_msg.html",
                {
                    'result': result,
                    'result1': result1,

                    'stats': stats,
                    'stats1': stats1,

                    'media_count': media_count,
                    'msg_deleted_count': msg_deleted_count,

                    'voice_call_count': voice_call_count,
                    'video_call_count': video_call_count,

                    'posneg': posneg,

                    'topic_modelling': topic_modelling,

                    'dataset_topic': dataset_topic,

                    'wordclouds': wordclouds,
                }
            )

        except Exception as e:

            print("WhatsApp processing error:")
            print(e)

            return HttpResponse(
                f"Error while processing WhatsApp file:<br><br>{str(e)}"
            )


# ============================================================
# FINAL RESULT
# ============================================================

class finalresult(View):

    template_name = 'process.html'

    def get(self, request, *args, **kwargs):

        print("Inside Get")

        try:

            dataset = pd.read_csv(
                'processed.csv'
            )

            dataset = dataset.dropna()

            return render(
                request,
                self.template_name,
                {
                    'dataset': dataset
                }
            )

        except FileNotFoundError:

            return HttpResponse(
                "processed.csv not found. Please upload and process a WhatsApp chat first."
            )

        except Exception as e:

            return HttpResponse(
                f"Error loading processed data: {str(e)}"
            )

    def post(self, request, *args, **kwargs):

        print("Inside Post")

        return redirect(
            reverse_lazy('result')
        )


# ============================================================
# SUCCESS
# ============================================================

class Success(TemplateView):

    template_name = 'succ_msg.html'


# ============================================================
# FAILURE
# ============================================================

class Failure(TemplateView):

    template_name = 'fail.html'


# ============================================================
# FILE NOT FOUND
# ============================================================

class FileNotfound(TemplateView):

    template_name = 'filenot.html'


# ============================================================
# ABOUT US
# ============================================================

class AboutUs(TemplateView):

    template_name = 'aboutus.html'