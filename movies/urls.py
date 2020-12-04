from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^register/', UserRegistrationView.as_view()),
    url(r'^movies/', get_movies),
    url(r'^collection/(?P<collection_uuid>.*)/', CollectionView.as_view()),
    url(r'^collection/', CollectionView.as_view()),
    url(r'^request-count/', ServerRequestCount.as_view()),
    url(r'^request-count/reset/', ServerRequestCount.as_view()),

]
