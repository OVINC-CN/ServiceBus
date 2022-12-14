import datetime

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.account.exceptions import WrongSignInParam, WrongToken
from apps.account.models import User, UserProperty
from apps.account.serializers import (
    SearchUserSerializer,
    SignInSerializer,
    UserInfoSerializer,
    UserListSerializer,
    UserPropertyCreateSerializer,
    UserPropertyDeleteSerializer,
    UserPropertyRequestSerializer,
    UserPropertySerializer,
    UserRegistrySerializer,
    VerifyUserTokenRequestSerializer,
)
from core.auth import ApplicationAuthenticate, SessionAuthenticate
from core.utils import get_auth_token, remove_auth_token
from core.viewsets import ListMixin, MainViewSet

USER_MODEL: User = get_user_model()


class UserInfoViewSet(MainViewSet):
    """
    User Info
    """

    queryset = USER_MODEL.get_queryset()
    serializer_class = UserInfoSerializer

    def list(self, request, *args, **kwargs):
        """
        Get User Info
        """

        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)


class UserPropertyViewSet(MainViewSet):
    """
    User Property
    """

    queryset = UserProperty.get_queryset()
    serializer_class = UserPropertySerializer

    def list(self, request, *args, **kwargs):
        """
        Get User Properties
        """

        # Validate Request Data
        request_serializer = UserPropertyRequestSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # Filter Properties
        properties = request.user.list_properties(request_data.get("key"))

        # Response Data
        serializer = UserPropertySerializer(instance=properties, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create User Property
        """

        # Validate Request Data
        request_serializer = UserPropertyCreateSerializer(data=request.data, many=True)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # Create Property
        properties = request.user.set_properties(request_data)

        # Response Data
        serializer = self.get_serializer(instance=properties, many=True)
        return Response(serializer.data)

    @action(methods=["DELETE"], detail=False)
    def bulk_destroy(self, request, *args, **kwargs):
        """
        Delete User Property
        """

        # Validate Request Data
        request_serializer = UserPropertyDeleteSerializer(data=request.data, context={"user": request.user})
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # Delete Property
        request.user.del_properties(request_data["property_keys"])
        return Response()


class UserSignViewSet(MainViewSet):
    """
    User Login and Logout
    """

    queryset = USER_MODEL.get_queryset()

    @action(methods=["POST"], detail=False, authentication_classes=[SessionAuthenticate])
    def sign_in(self, request, *args, **kwargs):
        """
        Sign in
        """

        # Validate Request Data
        request_serializer = SignInSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # login
        user = auth.authenticate(request, **request_data)
        if not user:
            raise WrongSignInParam()
        user.last_login = datetime.datetime.now()
        user.save(update_fields=["last_login"])

        # auth session
        response = Response()
        response.set_cookie(
            key=settings.AUTH_TOKEN_NAME,
            value=get_auth_token(user.username, settings.SESSION_COOKIE_AGE),
            expires=settings.SESSION_COOKIE_AGE,
            domain=settings.SESSION_COOKIE_DOMAIN,
        )

        return response

    @action(methods=["GET"], detail=False)
    def sign_out(self, request, *args, **kwargs):
        """
        Sign out
        """

        # Remove Session Cookie
        response = Response()
        response.delete_cookie(settings.AUTH_TOKEN_NAME, domain=settings.SESSION_COOKIE_DOMAIN)

        # Remove Cache
        remove_auth_token(request.user.username, request.COOKIES.get(settings.AUTH_TOKEN_NAME))

        return response

    @action(methods=["POST"], detail=False, authentication_classes=[SessionAuthenticate])
    def sign_up(self, request, *args, **kwargs):
        """
        sign up
        """

        # validate request
        request_serializer = UserRegistrySerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # save
        user = USER_MODEL.objects.create_user(last_login=datetime.datetime.now(), **request_data)

        # login session
        response = Response()
        response.set_cookie(
            key=settings.AUTH_TOKEN_NAME,
            value=get_auth_token(user.username, settings.SESSION_COOKIE_AGE),
            expires=settings.SESSION_COOKIE_AGE,
            domain=settings.SESSION_COOKIE_DOMAIN,
        )

        # response
        return response

    @action(methods=["POST"], detail=False, authentication_classes=[ApplicationAuthenticate])
    def verify_token(self, request, *args, **kwargs):
        """
        Verify User Token
        """

        # Validate Request Data
        request_serializer = VerifyUserTokenRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        request_data = request_serializer.validated_data

        # Check Token
        user = auth.authenticate(request, **request_data)
        if not user:
            raise WrongToken()

        # Response
        serializer = UserInfoSerializer(instance=user)
        return Response(serializer.data)


class UserSearchViewSet(ListMixin, MainViewSet):
    """
    Search User
    """

    queryset = USER_MODEL.get_queryset()

    def list(self, request, *args, **kwargs):
        """
        search
        """

        # validate request
        request_serializer = SearchUserSerializer(data=request.query_params)
        request_serializer.is_valid(raise_exception=True)
        keyword = request_serializer.validated_data["keyword"]

        # queryset
        queryset = USER_MODEL.objects.all()
        if keyword:
            queryset = queryset.filter(username__icontains=keyword)

        # response
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)
