from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .constants import MAX_FIELD_LENGTH, CUT_BOUNDARY_STR

User = get_user_model()


class CreatedAtModel(models.Model):
    """Абстрактная модель с полем даты создания."""
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class PublishedAndCreatedAtModel(CreatedAtModel):
    """Абстрактная модель с полями публикации и даты создания."""
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )

    class Meta(CreatedAtModel.Meta):
        abstract = True


class Category(PublishedAndCreatedAtModel):
    title = models.CharField("Заголовок", max_length=MAX_FIELD_LENGTH)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; "
                  "разрешены символы латиницы, цифры, дефис и подчёркивание."
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:CUT_BOUNDARY_STR]


class Location(PublishedAndCreatedAtModel):
    name = models.CharField(
        "Название места",
        max_length=MAX_FIELD_LENGTH
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name[:CUT_BOUNDARY_STR]


class Post(PublishedAndCreatedAtModel):
    title = models.CharField("Заголовок", max_length=MAX_FIELD_LENGTH)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text="Если установить дату и время в будущем"
        " — можно делать отложенные публикации.",
        default=timezone.now
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Категория",
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Местоположение",
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to="posts/",
        verbose_name="Изображение",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ['-pub_date']

    def __str__(self):
        return self.title[:CUT_BOUNDARY_STR]


class Comment(CreatedAtModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Публикация"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор"
    )
    text = models.TextField(
        "Текст комментария",
        help_text="Введите текст комментария"
    )

    class Meta(CreatedAtModel.Meta):
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

    def __str__(self):
        return self.text[:CUT_BOUNDARY_STR]
