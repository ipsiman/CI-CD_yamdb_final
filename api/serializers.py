from rest_framework import serializers

from api.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Класс для преобразования данных пользователя."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'bio', 'email', 'role')


class CategorySerializer(serializers.ModelSerializer):
    """Класс для преобразования данных категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Класс для преобразования данных жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializerGet(serializers.ModelSerializer):
    """Класс для преобразования данных произведения при методе GET."""

    category = CategorySerializer(many=False, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializerCreateAndUpdate(serializers.ModelSerializer):
    """
    Класс для преобразования данных произведения при методе CREATE и UPDATE.
    """

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Класс для преобразования данных отзыва."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        many=False
    )

    def validate(self, attrs):
        author = self.context['request'].user.id,
        title = self.context['view'].kwargs.get('title_id')
        message = 'Author review already exist'
        if not self.instance and Review.objects.filter(
                title=title,
                author=author
        ).exists():
            raise serializers.ValidationError(message)
        return attrs

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)


class CommentSerializer(serializers.ModelSerializer):
    """Класс для преобразования данных комментария."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        many=False
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment
