from django.urls import path, include
from rest_framework import routers
from .views import UploadViewSet, FetchNews, NewsLookupSet, GetFilter, GetSentimentSplit

router = routers.DefaultRouter()
router.register(r'upload', UploadViewSet, basename="upload")
router.register(r'fetch_news', FetchNews, basename="fetch_news")
router.register(r'get_news', NewsLookupSet, basename="get_news")
router.register(r'get_filter', GetFilter, basename="get_filter")
router.register(r'get_sentiment_split', GetSentimentSplit, basename="get_sentiment_split")

# router.register(r'get_news', NewsLookupSet, basename="get_news")

# Wire up our API using automatic URL routing.
urlpatterns = [
    path('', include(router.urls)),
]