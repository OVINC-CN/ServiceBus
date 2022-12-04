from django.core.files.uploadedfile import TemporaryUploadedFile
from django.utils.translation import gettext, gettext_lazy
from rest_framework import serializers

from apps.cos.constants import COSFileSizeLimit
from core.constants import MEDIUM_CHAR_LENGTH


class COSUploadAvatarSerializer(serializers.Serializer):
    """
    COS Upload
    """

    file = serializers.FileField(label=gettext_lazy("File"), max_length=MEDIUM_CHAR_LENGTH)

    def validate_file(self, file: TemporaryUploadedFile) -> TemporaryUploadedFile:
        # check size
        if file.size > COSFileSizeLimit.AVATAR:
            raise serializers.ValidationError(
                gettext("Avatar Size Too Large => %.2fMB") % (file.size / 1024.0 / 1024.0)
            )
        return file
