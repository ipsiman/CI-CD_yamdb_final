from django.contrib import admin

from api.models import Category, Comment, Genre, Review, Title, User


class UserAdmin(admin.ModelAdmin):
    """Класс для отображения полей пользователя в админке."""

    list_display = (
        'pk', 'first_name', 'last_name', 'username', 'bio', 'email', 'role'
    )
    search_fields = ('bio',)
    empty_value_display = '-пусто-'


class CategoryAdmin(admin.ModelAdmin):
    """Класс для отображения полей категории в админке."""

    list_display = ('pk', 'name', 'slug',)


class GenreAdmin(admin.ModelAdmin):
    """Класс для отображения полей жанра в админке."""

    list_display = ('pk', 'name', 'slug',)


class TitleAdmin(admin.ModelAdmin):
    """Класс для отображения полей произведения в админке."""

    list_display = ('pk', 'name', 'year', 'description', 'category',)
    filter_horizontal = ('genre',)
    search_fields = ('description',)
    list_filter = ('year',)
    empty_value_display = '-пусто-'


class ReviewAdmin(admin.ModelAdmin):
    """Класс для отображения полей отзыва в админке."""

    list_display = ('pk', 'text', 'author', 'score', 'pub_date', 'title',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """Класс для отображения полей комментария в админке."""

    list_display = ('pk', 'text', 'author', 'pub_date', 'review',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
