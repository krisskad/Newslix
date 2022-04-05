from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from .serializers import UploadSerializer, FetchNewsSerializer
from .models import NewsTimeSeries, Author, Publication, Category, Country
from django.core.files.storage import FileSystemStorage
import pandas as pd
from django.db import transaction
import numpy as np
import requests
from datetime import datetime
from django.db.models import Q, Count, Sum
from operator import and_, or_
from functools import reduce
from .helpers import get_word_freq
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from cleantext import clean

import os
from django.conf import settings

####################
nltk.data.path.append(os.path.join(settings.BASE_DIR, 'storage'))
####################

try:
  sia = SentimentIntensityAnalyzer()
except:
  nltk.download("vader_lexicon", download_dir=os.path.join(settings.BASE_DIR, 'storage'))
  sia = SentimentIntensityAnalyzer()


# # Create your views here.
class UploadViewSet(ViewSet):
    serializer_class = UploadSerializer
    queryset = NewsTimeSeries.objects.all()

    def list(self, request):
        queryset = NewsTimeSeries.objects.all().values(
            "date",
            "category__name",
            "author__name",
            "publication__name",
            "title",
            "description",
            "content",
            "source_url",
            "image_url",
        )[:5]
        return Response(queryset)

    def create(self, request):
        # file_uploaded = request.FILES.get('file_uploaded')
        # print(request.FILES)
        request_file = request.FILES['file_uploaded'] if 'file_uploaded' in request.FILES else None
        if request_file:
            # save attached file

            # create a new instance of FileSystemStorage
            fs = FileSystemStorage()
            file = fs.save(request_file.name, request_file)
            # the fileurl variable now contains the url to the file. This can be used to serve the file when needed.
            file_path = fs.path(request_file.name)

            if "xlsx" in request_file.name:
                df = pd.read_excel(file_path)

            elif "csv" in request_file.name:
                df = pd.read_csv(file_path)

            else:
                return Response("File format not supported")

            fields = ["title", "content", "date"]

            if all([x in df.columns for x in fields]):
                with transaction.atomic():
                    c=0
                    df = df.fillna("None")
                    df = df.dropna(subset=["title"])
                    df = df.dropna(subset=["date"])

                    for row in df.to_dict(orient="records"):
                        author = row.get("author", None)
                        publication = row.get("publication", None)
                        category = row.get("category", None)

                        if not author == np.nan or author == "nan" or author == "" or author == None or author == "None":
                            author = author.lower().strip()
                        else:
                            author = None

                        if not publication  == np.nan or publication == "nan" or publication == "" or publication == None or publication == "None":
                            publication = publication.lower().strip()
                        else:
                            publication = None

                        if not category  == np.nan or category == "nan" or category == "" or category == None or category == "None":
                            category = category.lower().strip()
                        else:
                            category = None

                        title = row["title"].strip()
                        content = row["content"].strip()

                        if "description" in row:
                            description = row["description"].strip()
                        else:
                            description = None

                        if "source_url" in row:
                            source_url = row["source_url"].strip()
                        else:
                            source_url = None

                        if "image_url" in row:
                            image_url = row["image_url"].strip()
                        else:
                            image_url = None

                        date = str(row["date"]).strip()

                        if date[0].isnumeric():
                            if "/" in date:
                                date = date.replace("/", "-")

                            if " " in date:
                                date = date.replace(" ", "-")

                            if author is None:
                                author_ins = None
                            else:
                                author_ins, created = Author.objects.get_or_create(name=author)

                            if publication is None:
                                publication_ins = None
                            else:
                                publication_ins, created = Publication.objects.get_or_create(name=publication)

                            if category is None:
                                category_ins = None
                            else:
                                category_ins, created = Category.objects.get_or_create(name=category)

                            title = clean(title,
                                  fix_unicode=True,  # fix various unicode errors
                                  to_ascii=True,  # transliterate to closest ASCII representation
                                  lower=True)

                            description = clean(description,
                                          fix_unicode=True,  # fix various unicode errors
                                          to_ascii=True,  # transliterate to closest ASCII representation
                                          lower=True)

                            content = clean(content,
                                          fix_unicode=True,  # fix various unicode errors
                                          to_ascii=True,  # transliterate to closest ASCII representation
                                          lower=True)

                            ts = NewsTimeSeries.objects.create(
                                author=author_ins,
                                publication=publication_ins,
                                title = title,
                                content=content,
                                date=date,
                                source_url=source_url,
                                image_url=image_url,
                                description=description,
                                category = category_ins
                            )
                            c=c+1

                return Response(f"Total : {len(df)}, uploaded : {c}")
            else:
                return Response(f"Columns not exist")
        else:
            return Response(f"file not uploaded")


class FetchNews(ViewSet):
    serializer_class = FetchNewsSerializer

    def list(self, request):
        queryset = NewsTimeSeries.objects.all().order_by("-date")
        count = queryset.count()
        publications = list(Publication.objects.all().values_list("name", flat=True))
        category = list(Category.objects.all().values_list("name", flat=True))

        # print(start_date)

        queryset = {
            "USE CASE": "Search keyword, Filter by dates & get required response",
            "TIP": "Choose check box to get that data in response",
            "TOTAL RECORDS": f"{count}",
            "TOTAL CATEGORY": category,
            "TOTAL PUBLICATIONS": publications,

        }
        return Response(queryset)

    def post(self, request):
        url = request.data.get("url", None)
        category = request.data.get("category.category", None)
        country = request.data.get("country.country", None)
        # print(request.data)

        # result = NewsTimeSeries.objects.all()

        if url is None:
            category_name, created = Category.objects.get_or_create(id=category.lower())
            country_name, created = Country.objects.get_or_create(code=country.lower())
            # print(country_name.name, category_name.name)
            url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category_name.name}&apiKey=84897746d7224ce483c511b4d3178a17"
            # print(url)
        else:
            category_name = None
            country_name = None

        response = requests.request("GET", url)

        if response.status_code == 200:
            data = response.json()
            with transaction.atomic():
                for each in data["articles"]:
                    publication = each["source"]["name"]
                    author = each["author"]
                    title = each["title"]
                    description = each["description"]
                    source_url = each["url"]
                    image_url = each["urlToImage"]
                    date = each["publishedAt"]
                    content = each["content"]
                    date_obj = datetime.fromisoformat(date[:-1] + '+00:00')


                    ############
                    title = clean(str(title),
                                  fix_unicode=True,  # fix various unicode errors
                                  to_ascii=True,  # transliterate to closest ASCII representation
                                  lower=True)

                    description = clean(str(description),
                                        fix_unicode=True,  # fix various unicode errors
                                        to_ascii=True,  # transliterate to closest ASCII representation
                                        lower=True)

                    content = clean(str(content),
                                    fix_unicode=True,  # fix various unicode errors
                                    to_ascii=True,  # transliterate to closest ASCII representation
                                    lower=True)

                    all_data = str(title) + " | " + str(description) + " | " + str(content)
                    sentiment = sia.polarity_scores(all_data)
                    sentiment_compound = sentiment["compound"]
                    sentiment_neu = sentiment["neu"]
                    sentiment_neg = sentiment["neg"]
                    sentiment_pos = sentiment["pos"]
                    ############
                    # print(publication, author, date)
                    # break
                    if author is None:
                        author_ins = None
                    else:
                        author_ins, created = Author.objects.get_or_create(name=author.lower())

                    if publication is None:
                        publication_ins = None
                    else:
                        publication_ins, created = Publication.objects.get_or_create(name=publication.lower())

                    # print(author_ins, publication_ins)
                    # break

                    data = NewsTimeSeries.objects.filter(
                        author=author_ins,
                        publication=publication_ins,
                        title=title
                    )

                    if data.exists():
                        continue

                    ts = NewsTimeSeries.objects.get_or_create(
                        author=author_ins,
                        publication=publication_ins,
                        title=title,
                        content=content,
                        date=date_obj,
                        source_url=source_url,
                        image_url=image_url,
                        description=description,
                        country = country_name,
                        category = category_name,
                        sentiment_compound = sentiment_compound,
                        sentiment_neu = sentiment_neu,
                        sentiment_neg = sentiment_neg,
                        sentiment_pos = sentiment_pos
                    )

        return Response(response.json())


class NewsLookupSet(ViewSet):
    def list(self, request):
        queryset = NewsTimeSeries.objects.all().values(
            "country__name",
            "category__name",
            "author__name",
            "publication__name",
            "title",
            "content",
            "description",
            "source_url",
            "image_url",
            "sentiment_compound",
            "sentiment_pos",
            "sentiment_neg",
            "sentiment_neu",
            "date"

        ).order_by("-date")[:5]
        # start_date = queryset.last().date
        # end_date = queryset.first().date
        # count = queryset.count()
        # publications = list(Publication.objects.all().values_list("name", flat=True))
        # print(start_date)

        # queryset = {
        #     "USE CASE": "Search keyword, Filter by dates & get required response",
        #     "TIP": "Choose check box to get that data in response",
        #     "AVAILABLE DATE": f"{start_date} to {end_date}",
        #     "TOTAL RECORDS": f"{count}",
        #     "TOTAL PUBLICATIONS": publications
        # }
        return Response(queryset)

    def post(self, request):
        search = request.data.get("search", None)
        category = request.data.get("category", None)
        country = request.data.get("country", None)
        publication = request.data.get("publication", None)
        author = request.data.get("author", None)
        start_date = request.data.get("start_date", None)
        end_date = request.data.get("end_date", None)

        queryset = NewsTimeSeries.objects.all()

        if search:
            queryset = queryset.filter(reduce(or_, [Q(title__icontains=search), Q(content__icontains=search)]))

        if category:
            queryset = queryset.filter(category = category)

        if country:
            queryset = queryset.filter(country = country)

        if publication:
            queryset = queryset.filter(publication = publication)

        if author:
            queryset = queryset.filter(author = author)

        if start_date is None and end_date is None:
            queryset = queryset.filter(date__gte = datetime.now().date())

        else:
            if start_date:
                queryset = queryset.filter(date__gte=start_date)

            if end_date:
                queryset = queryset.filter(date__lte=end_date)

        response = queryset.values(
            "country__name",
            "category__name",
            "author__name",
            "publication__name",
            "title",
            "content",
            # "description",
            "source_url",
            "image_url",
            "sentiment_compound",
            # "sentiment_pos",
            # "sentiment_neg",
            # "sentiment_neu",
            "date"
        ).order_by("date")

        if queryset.exists():
            # print(result)
            if queryset.count() > 100:
                response = queryset[:100]

            df = pd.DataFrame.from_dict(response)

            df['content'] = df['content'].fillna(df['description'])

            kwd = get_word_freq(df)
            # kwd = kwd[kwd["value"] > 1]
            # print(kwd)
            result = kwd[:10].to_dict(orient="records")

            # print(result)
            context = {
                "news":df.to_dict(orient="records"),
                "trend":result
            }
            return Response(context)
        else:
            context = {
                "news":[],
                "trend": []
            }
            return Response(context)


class GetFilter(ViewSet):

    def list(self, request):
        queryset = NewsTimeSeries.objects.all().order_by("-date")

        date = {"start_date":queryset.last().date, "end_date":queryset.first().date}
        country = Country.objects.values("name", "id")
        category = Category.objects.values("name", "id")
        author = Author.objects.values("name", "id")
        publication = Publication.objects.values("name", "id")

        response = {
            "date":date,
            "country":country,
            "category":category,
            "author":author,
            "publication":publication
        }
        return Response(response)


class GetSentimentSplit(ViewSet):

    def list(self, request):

        response = {
            "s":1
        }
        return Response(response)

    def post(self, request):
        search = request.data.get("search", None)
        category = request.data.get("category", None)
        country = request.data.get("country", None)
        publication = request.data.get("publication", None)
        author = request.data.get("author", None)
        start_date = request.data.get("start_date", None)
        end_date = request.data.get("end_date", None)

        queryset = NewsTimeSeries.objects.all()

        if search:
            queryset = queryset.filter(reduce(or_, [Q(title__icontains=search), Q(content__icontains=search)]))

        # if category:
        #     queryset = queryset.filter(category = category)

        if country:
            queryset = queryset.filter(country = country)

        if publication:
            queryset = queryset.filter(publication = publication)

        if author:
            queryset = queryset.filter(author = author)

        if start_date is None and end_date is None:
            queryset = queryset.filter(date__gte=datetime.now().date())

        else:
            if start_date:
                queryset = queryset.filter(date__gte=start_date)

            if end_date:
                queryset = queryset.filter(date__lte=end_date)

        category = queryset.values("category__id", "category__name")

        context = {}

        for each in category:
            positive = queryset.filter(category=each["category__id"], sentiment_compound__gt=0.25).count()
            negative = queryset.filter(category=each["category__id"], sentiment_compound__lt=-0.25).count()
            neutral = queryset.filter(
                category=each["category__id"],
                sentiment_compound__gte=-0.25,
                sentiment_compound__lte=0.25).count()
            total = positive + negative + neutral
            context[each["category__name"]] = {
                "total": total,
                "positive":positive,
                "negative":negative,
                "neutral":neutral,
                "id":each["category__id"],
            }

        context["total_positive"] = queryset.filter(sentiment_compound__gt=0.25).count()
        context["total_negative"] = queryset.filter(sentiment_compound__lt=-0.25).count()
        context["total_neutral"] = queryset.filter(
            sentiment_compound__gte=-0.25,
            sentiment_compound__lte=0.25
        ).count()
        context["total"] = context["total_positive"] + context["total_negative"] + context["total_neutral"]

        return Response(context)

