from django.conf.urls import url
from appserver import views as app_view
from rest_framework_jwt.views import obtain_jwt_token
# from django.contrib.auth import views as auth_views
# from django.views.generic import RedirectView

urlpatterns = [
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^$', app_view.Login_view, name='login'),
    url(r'^home/$', app_view.home, name='home'),
    url(r'^logout/$', app_view.Wlogout, name='logout'),

    # url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    # url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    # url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

    url(r'^user/$', app_view.UserList.as_view(), name='user-list'),
    url(r'^user/(?P<pk>[0-9]+)/$', app_view.UserDetail.as_view()),
    url(r'^mlogout/', app_view.MLogout.as_view()),
    url(r'^profile-edit/$', app_view.ProfileEdit, name='editProfile'),
    url(r'^profile/$', app_view.Profile, name='Profile'),
    url(r'^list-docs/$', app_view.ListOutDocument, name='listDocument'),
    url(r'^basic-upload/$', app_view.BasicUploadView.as_view(), name='basic_upload'),
    url(r'^getall/$', app_view.getall, name='dashboard'),
    url(r'^edit/(?P<id>[0-9]+)/$', app_view.edit),
    url(r'^update/(?P<id>[0-9]+)/$', app_view.update),
    url(r'^delete/(?P<id>[0-9]+)/$', app_view.destroy),
    url(r'^upload/$', app_view.upload, name='uploading'),

    url(r'^download/$', app_view.download, name="download_mod"),

]
