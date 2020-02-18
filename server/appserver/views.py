# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from zipfile import ZipFile
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from appserver.serializers import UserSerializer, DocumentSerializer, OverallScoreSerializer
from appserver.forms import LoginForm, LoginNewForm, DashboardForm, DocumentForm
from appserver.models import Document, OverallScore
from django.views import generic
from django.views.generic import View
from django.contrib.auth import authenticate, logout, get_user_model, login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from datetime import datetime, timedelta
import pandas as pd
from django.utils import timezone
import shutil
import os
from main_engine import Getting_Score_Result

# from django.shortcuts import render_to_response, get_object_or_404
# from django.http import Http404, HttpResponse
# from django.template.loader import render_to_string
# from django.core.mail import send_mail
# from rest_framework.decorators import api_view
# from django.views.decorators.csrf import csrf_protect
# from django.template import RequestContext

# from language_assessment_acs.language_assessment_core import main_engine

# Global declaration of operation folder
ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#print("ROOT_FOLDER -->", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# sys.path.append("/home/shantakumar/Projects/git_lab_proj/language_assessment_acs/language_assessment_core/")
#
# sys.path.insert(0, ROOT_FOLDER)

# sys.path.append('../')
#

# Create your views here.
# import datetime


def Login_view(request):
    if request.method == 'POST':
        # POST, generate form with data from the request
        form = LoginNewForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        # uri = '/profile/user/'
        if user is not None and user.is_active:
            login(request, user)
            return redirect('appserver:dashboard')
            # return render(request, 'home.html', {"user" : user})
        else:
            form = LoginNewForm()
            return render(request, 'registration/login.html', {'form': form, 'errormessage': True})
    else:
        # GET, generate blank form
        form = LoginNewForm()
        return render(request, 'registration/login.html', {'form': form})


class LoginView(generic.FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'registration/login.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        print("user --->", user)
        uri = '/profile/user/'
        if user is not None and user.is_active:
            login(self.request, user)
            return render(self.request, 'home.html', {"user": user})

            if not user.is_staff:
                if self.request.GET.get('next') is not None and self.request.GET.get('next') != '':
                    uri = uri + '?next=' + self.request.GET.get('next')
                return redirect(uri)

            if self.request.GET.get('next') is not None and self.request.GET.get('next') != '':
                return redirect(self.request.GET.get('next'))

            return super(LoginView, self).form_valid(form)
        else:
            User = get_user_model()
            print(User._meta.fields)
            return self.form_invalid(form)


@login_required(login_url='appserver:login')
def home(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        return render(request, 'home.html', {'user': user})
    else:
        return render(request, 'home.html', {})


def Wlogout(request):
    logout(request)
    return redirect('/')


# @api_view(['GET', 'POST', ])
def ListOutDocument(request, format=None):
    # print "inside predict web function", request.POST['title']
    if request.method == 'POST':
        form = DashboardForm(request.POST)

        if request.FILES:
            test_file_obj = request.FILES['testfile']
            # print("test file obj -->", test_file_obj )
            # resp = analysis_modeling(request, test_file_obj) # functon from doc analysis
            # resp = True

        else:
            resp = True

        return render(request, 'home.html', {"Result": resp})  # 'form':form


class BasicUploadView(View):
    def get(self, request):
        photos_list = Document.objects.all().order_by('-uploaded_at')
        print(photos_list)
        return render(self.request, 'uploadIndex.html', {'photos': photos_list})

    def post(self, request):
        form = DocumentForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()
            data = {'is_valid': True, 'name': photo.document.name, 'url': photo.document.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def get_request_user_group(request):
    request_user_groups = request.user.groups.all()
    if request_user_groups:
        request_user_group = request_user_groups[0]
    else:
        request_user_group = Group.objects.get(name='default')

    return request_user_group


@login_required(login_url='appserver:login')
def getall(request):
    request_user_group = get_request_user_group(request)
    print("get_request_user_group ---> ", request_user_group)
    score_data = OverallScore.objects.filter(created_by=request_user_group).order_by('-created_at')
    # score_data = OverallScore.objects.all().order_by('-created_at')
    score_list = []
    for sc in score_data:
        score_dict = {}
        score_dict['document'] = sc.document.name
        score_dict['document_id'] = sc.document.id
        score_dict['grammer_language'] = sc.grammer_language
        score_dict['no_of_words'] = sc.no_of_words
        score_dict['journal_title'] = sc.journal_title
        score_dict['author_nationality'] = sc.author_nationality
        score_dict['article_type'] = sc.article_type
        score_dict['overall_score'] = sc.score
        score_dict['topic'] = sc.document.expect_topic if sc.document.is_edit else sc.document.obtain_topic
        # datetime.datetime.strptime(sc.document.uploaded_at, "%Y/%m/%d") if sc.document.uploaded_at else ""
        score_dict['create_date'] = sc.document.uploaded_at.strftime("%d/%m/%Y") if sc.document.uploaded_at else " "
        # datetime.datetime.strptime(sc.document.modified_at, "%Y/%m/%d") if sc.document.modified_at else ""
        score_dict['modified_date'] = sc.document.modified_at.strftime("%d/%m/%Y") if sc.document.modified_at else " "
        score_list.append(score_dict)

    return render(request, 'getAll.html', {'scores': score_list})


@login_required(login_url='appserver:login')
def edit(request, id):
    document = Document.objects.get(id=id)
    return render(request, 'edit.html', {'document': document})


@login_required(login_url='appserver:login')
def upload(request, format=None):

    request_user_group = get_request_user_group(request)
    # print("upload_request_user_group ---> ", request_user_group.id)
    if request.method == 'POST':
        # form = DashboardForm(request.POST)
        if request.FILES:
            zip_file_obj = request.FILES['testfile']
            # print("test file obj -->", zip_file_obj)
            with ZipFile(zip_file_obj, 'r') as zip:
                # zip.printdir()
                zip_dir_list = zip.namelist()
                zip.extractall(settings.TEMP_UPLOAD_DIR_ROOT)
            zip.close()
            document_files = [x for x in zip_dir_list if x.endswith(('.doc', '.docx', '.DOC', '.DOCX'))]

            for doc in document_files:
                abs_doc_path = os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, doc)
                doc_dir_path = os.path.join(settings.TEMP_UPLOAD_DIR_ROOT, doc.rsplit("/", 1)[0])
                result_df, file_topic_df = Getting_Score_Result(doc_dir_path, abs_doc_path)

                # topic_insert_cmd = "INSERT INTO appserver_document (uploaded_at, is_edit, abstract, expect_topic, name, obtain_topic, title, modified_at, file_path) VALUES (%s, '0', %s, %s, %s, %s, %s, NULL, %s);"
                # topic_insert_val = (datetime.datetime.now(tz=timezone.utc), str(file_topic_df['Abstract'][0]).encode('ascii', 'ignore').decode('ascii'), str(result_df['Topic'][0]),  str(
                #     file_topic_df['File Name'][0]), str(result_df['Topic'][0]), str(file_topic_df['Title'][0]).encode('ascii', 'ignore').decode('ascii'), path)
                # cursor.execute(topic_insert_cmd, topic_insert_val)
                #
                # score_insert_cmd = "INSERT INTO appserver_overallscore (grammer_language,no_of_words,journal_title,author_nationality,article_type,score,created_at,document_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
                # score_insert_val = (str(result_df['Lang/Grammar'][0]), str(result_df['No of words'][0]), str(result_df['Journal code'][0]),
                #                     str(result_df['author nation'][0]), str(result_df['article type'][0]), result_df['Obtained Level'][0], datetime.datetime.now(), doc_id)

                doc_req_data = {"uploaded_at": datetime.now(), "is_edit": False, "abstract": str(
                    file_topic_df['Abstract'][0]).encode('ascii', 'ignore').decode('ascii'), "expect_topic": str(result_df['Topic'][0]),
                    "name": str(file_topic_df['File Name'][0]), "obtain_topic": str(result_df['Topic'][0]), "title": str(file_topic_df['Title'][0]).encode('ascii', 'ignore').decode('ascii'),
                    "modified_at": None, "file_path": abs_doc_path}

                doc_serializer = DocumentSerializer(data=doc_req_data)
                if doc_serializer.is_valid():
                    doc_serializer.save()

                    score_req_data = {"document": doc_serializer.data['id'], "grammer_language": str(result_df['Lang/Grammar'][0]), "no_of_words": str(result_df['No of words'][0]),
                                      "journal_title": str(result_df['Journal code'][0]), "author_nationality": str(result_df['author nation'][0]), "article_type": str(result_df['article type'][0]),
                                      "score": result_df['Obtained Level'][0], "created_at": datetime.now(), "created_by": request_user_group.id}

                    score_serializer = OverallScoreSerializer(data=score_req_data)
                    if score_serializer.is_valid():
                        score_serializer.save()
                        # print("score_serializer -->", score_serializer.data)
                else:
                    return render(request, 'upload.html', {'upload_status': False})

            return render(request, 'upload.html', {'upload_status': True})
        else:
            pass
    return render(request, 'upload.html', {'upload_status': False})


@login_required(login_url='appserver:login')
def update(request, id):
    doc_obj = Document.objects.get(id=id)
    # name = request.POST['name']
    # title =  request.POST['title']
    # abstract = request.POST['abstract']
    topic = request.POST['topic']
    is_edit = False if topic == doc_obj.obtain_topic else True

    req_data = {"expect_topic": topic, "is_edit": is_edit, "modified_at": datetime.now(tz=timezone.utc)}

    serializer = DocumentSerializer(doc_obj, data=req_data)
    if serializer.is_valid():
        serializer.save()
        score_objs = OverallScore.objects.filter(document=doc_obj)
        # print(score_objs)
        for sc_obj in score_objs:
            # ce =  ((0.2  a1[0])+(0.2  a2) + (.25  b) + (0.1  c) + (.15  d) + (.1  e))
            ce = ((0.2 * sc_obj.grammer_language) + (0.2 * sc_obj.document.expect_topic) + (0.25 * sc_obj.no_of_words) +
                  (0.1 * sc_obj.journal_title) + (0.15 * sc_obj.author_nationality) + (0.1 * sc_obj.article_type))

            if (ce <= 1.66):
                obtained_level = 'EASY'
            elif (ce <= 2.33):
                obtained_level = 'INTERMEDIATE'
            else:
                obtained_level = 'DIFFICULT'

            sc_obj.score = obtained_level
            sc_obj.save()

            # mod_file = sc_obj.document.file_path.split('/')[-1]
            # print("mod_file --->", mod_file)

        return redirect("/getall")

    # form = DocumentEditForm(request.POST, instance = document)
    # if form.is_valid():
    #     form.cleaned_data['is_edit']  = True
    #     update_form = form.save()
    #     print(update_form.is_edit, update_form.score )
    #     return redirect("/basic-upload")
    return render(request, 'edit.html', {'document': doc_obj})


@login_required(login_url='appserver:login')
def destroy(request, id):
    document = Document.objects.get(id=id)
    overscore_obj = OverallScore.objects.get(document=document)

    dir_path = document.file_path

    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

    overscore_obj.delete()
    document.delete()

    return redirect("/getall")
    # return redirect("/basic-upload")


@login_required(login_url='appserver:login')
def download(request):
    from_date = request.GET['from_date']
    to_date = request.GET['to_date']
    from_dt_obj = datetime.strptime(from_date, '%d/%m/%Y')
    to_dt_obj = datetime.strptime(to_date, '%d/%m/%Y') + timedelta(days=1)

    # print("from_date_obj , to_date_obj -->",from_dt_obj ,to_dt_obj)
    request_user_group = get_request_user_group(request)

    mod_doc_objs = OverallScore.objects.filter(created_by=request_user_group, created_at__gte=from_dt_obj, created_at__lte=to_dt_obj).values(
        'document__modified_at', 'document__file_path', 'document__expect_topic', 'document__name', 'document__title', 'grammer_language', 'no_of_words', 'journal_title', 'author_nationality', 'article_type', 'score', 'created_at')

    mod_df = pd.DataFrame.from_records(mod_doc_objs)

    # print("total lenth --->", len(mod_doc_objs), to_dt_obj)
    # print("mod_data_frame -->", mod_df)

    mod_df.rename(columns={'document__name': 'Document Name', 'grammer_language': 'Grammar Language', 'document__expect_topic': 'Topic',
                           'no_of_words': 'No of words', 'document__title': 'Document Title', 'journal_title': 'Journal Type', 'author_nationality': 'Author Nationality', 'article_type': 'Article Type',
                           'created_at': 'Created At', 'document__modified_at': 'Modified At', 'score': 'Class', 'document__file_path': 'File Path'
                           }, inplace=True)

    # ordering columns as order
    mod_df = mod_df[['Document Name', 'Class', 'Document Title', 'Grammar Language', 'Topic', 'No of words',
                     'Journal Type', 'Author Nationality', 'Article Type', 'Created At', 'Modified At', 'File Path']]

    # eliminating time zone
    mod_df['Created At'] = mod_df['Created At'].astype(str).str[:-6]
    mod_df['Modified At'] = mod_df['Modified At'].astype(str).str[:-6]

    # converting df to excel file to media
    mod_df.to_excel("./media/document_logs.xlsx", sheet_name='Filtered_logs', index=False)

    # serve the download link
    down_link = request.build_absolute_uri('{0}/{1}'.format(settings.MEDIA_URL, 'document_logs.xlsx'))

    return redirect(down_link)  # redirect("/getall")


class MLogout(APIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, )

    def get(self, request, format=None):
        logout(request)
        return Response({'success': True}, status=status.HTTP_200_OK)


class UserList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, )
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, )

    queryset = User.objects.all()
    serializer_class = UserSerializer


def ProfileEdit(request):
    if request.method == 'POST':
        # POST, generate form with data from the request
        username = request.user
        current_password = request.POST['currentpassword']
        new_password = request.POST['newpassword']
        confirm_password = request.POST['conformpassword']
        print("request user, password ", username, current_password, confirm_password)

        user = authenticate(username=username, password=current_password)
        print("user on profile edit --->", user)
        if user is not None and user.is_active and new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            return render(request, 'home.html', {"user": user, 'EditSucess': True})
        else:
            return render(request, 'registration/profile.html', {'EditFailure': True})
    else:
        form = LoginNewForm()
        return render(request, 'registration/login.html', {'form': form})


def Profile(request):
    print(request.user)
    context = {}
    return render(request, 'registration/profile.html', context)
