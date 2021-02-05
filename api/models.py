from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api.utils import validate_date_not_in_future


class UserRole(models.TextChoices):
    """Модель для представления роли пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


class User(AbstractUser):
    """Модель для представления пользователя."""

    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name='Электронная почта'
    )
    confirmation_code = models.CharField(
        max_length=99,
        blank=True,
        null=True,
        editable=False,
        unique=True,
        verbose_name='Код подтверждения'
    )
    bio = models.TextField(blank=True, verbose_name='О себе')
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Category(models.Model):
    """Модель для представления категории."""

    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, db_index=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для представления жанра."""

    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(
        unique=True,
        db_index=True,
        blank=True,
        verbose_name='Адрес'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для представления произведения."""

    name = models.CharField(max_length=200, verbose_name='Название')
    year = models.PositiveIntegerField(
        db_index=True,
        validators=[validate_date_not_in_future]
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        related_query_name='query_titles',
        verbose_name='Жанр',
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель для представления отзыва."""

    text = models.TextField(max_length=10000, blank=False, verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
        null=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('author', 'title',)
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author} - {self.title}'


class Comment(models.Model):
    """Модель для представления комментария."""

    text = models.TextField(max_length=2000, verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments',
        verbose_name='Отзыв'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
