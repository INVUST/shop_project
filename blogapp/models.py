from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    bio = models.TextField(verbose_name="Биография")

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name="Название")

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название")

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    pub_date = models.DateTimeField(verbose_name="Дата публикации")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="Автор",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name="Категория",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='articles',
        verbose_name="Тэги",
    )

    def __str__(self):
        return self.title