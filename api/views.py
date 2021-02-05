from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters import rest_framework
from rest_framework import (filters, mixins, permissions, status, views,
                            viewsets)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.models import Category, Comment, Genre, Review, Title, User
from api.permissions import (AdminPermission, ModeratorPermission,
                             ObjectAuthorPermission, ReadOnlyPermission)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleSerializerCreateAndUpdate,
                             TitleSerializerGet, UserSerializer)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_email(request):
    """Метод для отправки кода подтверждения на почту."""
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    user = User.objects.get_or_create(email=email)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Confirmation code from Yamdb',
        f'This is your confirmation code: {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )
    return Response('Your confirmation code was sent to your email')


class TokenGetView(views.APIView):
    """Класс для получения токена по коду подтверждения."""

    @permission_classes([permissions.AllowAny])
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.data['confirmation_code']
        user_email = serializer.data['email']
        user = get_object_or_404(User, email=user_email)
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': f'{token}'},
                status=status.HTTP_200_OK
            )
        return Response(
            'Неверный confirmation_code',
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Класс для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, AdminPermission]
    pagination_class = PageNumberPagination
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_fields = ['username']
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        if request.method == 'GET':
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryAndGenreMixin(mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Общий класс для категорий и жанров."""

    filter_backends = [filters.SearchFilter]
    permission_classes = [AdminPermission | ReadOnlyPermission]
    search_fields = ['=name']
    lookup_field = 'slug'


class CategoryViewSet(CategoryAndGenreMixin):
    """Класс для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryAndGenreMixin):
    """Класс для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Класс для работы с произведениями."""

    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = [AdminPermission | ReadOnlyPermission]
    http_method_names = ['get', 'post', 'delete', 'patch']
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update', 'destroy']:
            return TitleSerializerCreateAndUpdate
        return TitleSerializerGet


class ReviewViewSet(viewsets.ModelViewSet):
    """Класс для работы с оценками."""

    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        (ObjectAuthorPermission | AdminPermission | ModeratorPermission)
    ]

    def get_queryset(self):
        queryset = Review.objects.all()
        title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        if title is not None:
            queryset = Review.objects.filter(title=self.kwargs.get('title_id'))
        return queryset

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Класс для работы с комментариями."""

    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        (ObjectAuthorPermission | AdminPermission | ModeratorPermission)
    ]

    def get_queryset(self):
        queryset = Comment.objects.all()
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        if review is not None:
            queryset = Comment.objects.filter(
                review=self.kwargs.get('review_id'))
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)
