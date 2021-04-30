"""ERDAV URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import cache_page

from ERDAV import settings
from dataView import views
from utils.parse_yaml import global_config

cache_age = 60 * 2  # 缓存时间

if global_config.get('django'):
    # 全局配置文件
    cache_age = 60 * int(global_config.get('django').get('cache_age'))

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 当你在 URLconf 中使用 cache_page 时，可以这样包装视图函数。
    path('job/getJobsInfo', cache_page(cache_age)(views.getJobInfos)),
    path('job/AvgSalaryEveryCity', cache_page(cache_age)(views.getAvgSalaryEveryCity)),
    path('job/jobCountsEveryCity', cache_page(cache_age)(views.getJobCountsByEveryCity)),
    path('job/avgWage', cache_page(cache_age)(views.getAvgSalaryByCityAndJobType)),
    path('job/jobTypeCountOfCity', cache_page(cache_age)(views.getJobTypeCountByCity)),
    path('job/getEducationAndExperienceOfCity', cache_page(cache_age)(views.getEducationAndExperienceOfCity)),
    path('job/online_k_means', cache_page(cache_age)(views.online_k_means)),
    path('job/textRank', cache_page(cache_age)(views.get_t_r)),
    path('job/startApriori', cache_page(cache_age)(views.start_apriori)),
    path('job/random_forest_predict', cache_page(cache_age)(views.get_forest_predict)),

    # path('job/test_cache', views.test_cache),
    # path('job/test_cache2', cache_page(cache_age)(views.test_cache2))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
