from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cos.models import COSLog
from apps.cos.serializers import COSUploadAvatarSerializer
from apps.cos.utils import cos_client
from core.viewsets import MainViewSet


class COSViewSet(MainViewSet):
    """
    COS
    """

    queryset = COSLog.get_queryset()

    @action(methods=["POST"], detail=False)
    def upload_avatar(self, request, *args, **kwargs):
        """
        upload avatar
        """

        # validate request
        request_serializer = COSUploadAvatarSerializer(data=request.FILES)
        request_serializer.is_valid(raise_exception=True)
        request_file = request_serializer.validated_data["file"]

        # upload
        url = cos_client.upload(request, request_file, request_file.name)

        return Response({"url": url, "name": request_file.name})
