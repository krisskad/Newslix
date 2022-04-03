from rest_framework import serializers
from .models import NewsTimeSeries, Publication, Author, Country, Category


class UploadSerializer(serializers.Serializer):
    file_uploaded = serializers.FileField()

    class Meta:
        fields = ['file_uploaded']


class DatePickerSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    class Meta:
        fields = ['start_date', 'end_date']


class TextSerializer(serializers.Serializer):
    search = serializers.CharField()

    class Meta:
        fields = ['search',]


class CountrySerializer(serializers.Serializer):
    COUNTRY_CHOICES = list(Country.objects.all().values_list("code", "name"))
    country = serializers.ChoiceField(choices=COUNTRY_CHOICES)

    class Meta:
        fields = ['country',]


class PublicationSerializer(serializers.Serializer):
    PUBLICATIONS_CHOICES = list(Publication.objects.all().values_list("id", "name"))
    PUBLICATIONS_CHOICES.insert(0,(0, "all"))
    publication = serializers.ChoiceField(choices=PUBLICATIONS_CHOICES)

    class Meta:
        fields = ['publication',]


class CategorySerializer(serializers.Serializer):
    CATEGORY_CHOICES = list(Category.objects.all().values_list("id", "name"))
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)

    class Meta:
        fields = ['category',]


class FetchNewsSerializer(serializers.Serializer):
    url = TextSerializer()
    category = CategorySerializer()
    country = CountrySerializer()

    class Meta:
        fields = ['url','category', 'country']


class ChooseFeature(serializers.Serializer):
    location = serializers.BooleanField(default=False)
    mentioned = serializers.BooleanField(default=False)
    sentiment = serializers.BooleanField(default=False)

    class Meta:
        fields = ['location', 'mentioned', 'sentiment']


class ChoiceSerializer(serializers.Serializer):
    PUBLICATIONS_CHOICES = list(Publication.objects.all().values_list("id", "name"))
    PUBLICATIONS_CHOICES.insert(0,(0, "all"))
    publication = serializers.ChoiceField(choices=PUBLICATIONS_CHOICES)

    class Meta:
        fields = ['publication',]

class TextInputBoxSerializer(serializers.Serializer):
    search = TextSerializer()
    select = ChoiceSerializer()
    date = DatePickerSerializer()
    fetch = ChooseFeature()

    class Meta:
        fields = ['search', "date"]


class NewsTimeSeriesSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    publication = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = NewsTimeSeries
        fields = ["date", "author", "publication", "title", "content"]