from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('apps.CLI_Generator.views',
    url(r'^$', 'main'), 
    url(r'^convert/$', 'convert'), 
    url(r'^nexus_config_csv/download/$', 'download_nexus_config_csv'), 
    url(r'^nexus_config_generator/download/$', 'download_nexus_config_generator'), 
    url(r'^nexus_config_nxapi/convert/$', 'convert_nexus_config_nxapi'), 
    url(r'^nexus_config_puppet/convert/$', 'convert_nexus_config_puppet'),  
    url(r'^nexus_config_ansible/convert/$', 'convert_nexus_config_ansible'), 
)
