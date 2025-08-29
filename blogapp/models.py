from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя автора")
    bio = models.TextField(verbose_name="Биография")

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=20, verbose_name="Название тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    pub_date = models.DateTimeField(verbose_name="Дата публикации")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        blank=True
    )

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-pub_date']

    def __str__(self):
        return self.title