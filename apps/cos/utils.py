import datetime

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from qcloud_cos import CosConfig, CosS3Client
from rest_framework.request import Request

from apps.cos.models import COSLog
from core.exceptions import UploadFileFailed
from core.logger import logger
from core.utils import simple_uniq_id


class COSClient:
    """
    Manage COS Files
    """

    def __init__(self):
        self.config = CosConfig(
            Region=settings.COS_REGION,
            SecretId=settings.COS_SECRET_ID,
            SecretKey=settings.COS_SECRET_KEY,
        )
        self.client = CosS3Client(self.config)

    def upload(self, request: Request, file: TemporaryUploadedFile, filename: str, **kwargs) -> str:
        """
        upload file to cos and record log
        """

        # build path
        full_path = self._build_full_path(filename)
        logger.info("[UploadFileStart] File => %s; Path => %s; Kwargs => %s", file, full_path, kwargs)

        # Record Log
        cos_log = COSLog.objects.create(
            file_name=filename, file_path=full_path, file_size=file.size, extra_params=kwargs, upload_by=request.user
        )

        # Upload
        result = self._upload(file, full_path, **kwargs)
        cos_log.upload_result = result
        cos_log.save(update_fields=["upload_result"])

        # response
        if isinstance(result, dict) and result.get("ETag"):
            return f"{settings.COS_DOMAIN}{full_path}"
        raise UploadFileFailed()

    def _upload(self, file: TemporaryUploadedFile, full_path: str, **kwargs) -> dict:
        """
        upload file to cos
        """

        try:
            result = self.client.put_object(Bucket=settings.COS_BUCKET, Body=file, Key=full_path, **kwargs)
            logger.info("[UploadFileSuccess] Result => %s", result)
        except Exception as err:
            logger.error("[UploadFileFailed] Err => %s", err)
            result = err
        return result

    def _build_full_path(self, filename: str) -> str:
        """
        build path for file
        """

        # build path
        now = datetime.datetime.now()
        full_path = "{prefix}/{year}{month}/{day}/{uniq_id}/{filename}".format(
            prefix=settings.COS_FILE_PREFIX,
            year=now.year,
            month=now.month,
            day=now.day,
            uniq_id=simple_uniq_id(settings.COS_UNIQID_LENGTH),
            filename=filename,
        )

        # check path duplicated
        if COSLog.check_path(file_path=full_path):
            return full_path
        return self._build_full_path(filename)


cos_client = COSClient()
