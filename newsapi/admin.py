from django.contrib import admin
from django.contrib import admin

# Register your models here.
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from newsapi.models import *


class NewsTimeSeriesResource(resources.ModelResource):
    class Meta:
        model = NewsTimeSeries
        use_transactions = True
        # exclude = ('id',)
        # import_id_fields = ('skuid', 'category')
        # import_id_fields = ('skuid', 'category', 'retailer_client')

    def before_import_row(self, row, **kwargs):
        if row.keys():
            for col in row.keys():
                if "author" in col.lower():
                    author = row.get(col)
                    if author:
                        author = author.lower().strip()
                        author_ins = Author.objects.get_or_create(name=author)[0]
                        # author_ins = Author.objects.filter(name=author)
                        # if author_ins.exists():
                        #     author_ins = Author.objects.get(name=author)
                        # else:
                        #     ins = Author(name=author).save()
                        #     # Author.objects.create(name=author)
                        #     author_ins = Author.objects.filter(name=author)[0]

                        row['author'] = author_ins.id
                        break

            for col in row.keys():
                if "publication" in col.lower():
                    publication = row.get(col)
                    if publication:
                        publication = publication.lower().strip()
                        publication_ins = Publication.objects.get_or_create(name=publication)[0]
                        # publication_ins = Publication.objects.filter(name=publication)
                        # if publication_ins.exists():
                        #     publication_ins = Publication.objects.get(name=publication)
                        # else:
                        #     ins = Publication(name=publication).save()
                        #     # Publication.objects.create(name=publication)
                        #     publication_ins = Publication.objects.filter(name=publication)[0]

                        row['publication'] = publication_ins.id
                        break

            for col in row.keys():
                if "date" in col.lower():
                    date = row.get(col)
                    row['date'] = date.strip()
                    break

    def skip_row(self, instance, original):
        # print(str(instance.date))
        # print(original.date)
        if not str(instance.date)[0].isdigit():
            return True


@admin.register(NewsTimeSeries)
class NewsTimeSeriesResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'author', 'publication', 'title', 'description', 'content', 'source_url', 'image_url',  'date']
    search_fields = ['author', 'publication', 'title']
    list_filter = ['publication', ]
    resource_class = NewsTimeSeriesResource

    def author(self, obj):
        try:
            return obj.author.name
        except:
            return None

    def publication(self, obj):
        try:
            return obj.publication.name
        except:
            return None


class AuthorResource(resources.ModelResource):
    class Meta:
        model = Author
        use_transactions = True


@admin.register(Author)
class AuthorResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = AuthorResource


class PublicationResource(resources.ModelResource):
    class Meta:
        model = Publication
        use_transactions = True


@admin.register(Publication)
class PublicationResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = PublicationResource


class CountryResource(resources.ModelResource):
    class Meta:
        model = Country
        use_transactions = True


@admin.register(Country)
class CountryResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'created_on', 'updated_on']
    search_fields = ['name', 'code']
    resource_class = CountryResource


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        use_transactions = True


@admin.register(Category)
class CategoryResourceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    search_fields = ['name', ]
    resource_class = CategoryResource