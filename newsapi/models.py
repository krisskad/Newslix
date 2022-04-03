from django.db import models
from django.conf import settings
# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=160, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Authors"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Author, self).save(*args, **kwargs)


class Publication(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Publications"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Publication, self).save(*args, **kwargs)


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Countries"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Country, self).save(*args, **kwargs)


class State(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "States"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(State, self).save(*args, **kwargs)


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=5, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Cities"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(City, self).save(*args, **kwargs)


class Mentioned(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Mentioned"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Mentioned, self).save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if self.name:
            self.name = self.name.lower()
        return super(Category, self).save(*args, **kwargs)


class NewsTimeSeries(models.Model):
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    publication = models.ForeignKey(Publication, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    mentioned = models.ForeignKey(Mentioned, on_delete=models.SET_NULL, null=True)

    title = models.TextField()
    description = models.TextField(null=True)
    content = models.TextField(null=True)

    source_url = models.TextField(null=True)
    image_url = models.TextField(null=True)

    sentiment_compound = models.FloatField(null=True)
    sentiment_neu = models.FloatField(null=True)
    sentiment_neg = models.FloatField(null=True)
    sentiment_pos = models.FloatField(null=True)

    date = models.DateTimeField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = "NewsTimeSeries"
        unique_together = ('author', 'publication','title')