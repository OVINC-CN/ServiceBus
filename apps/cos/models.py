from django.db import models
from django.utils.translation import gettext_lazy

from core.constants import MAX_CHAR_LENGTH
from core.models import BaseModel, ForeignKey, UniqIDField


class COSLog(BaseModel):
    """
    COS Log
    """

    id = UniqIDField(gettext_lazy("ID"))
    file_name = models.CharField(gettext_lazy("File Name"), max_length=MAX_CHAR_LENGTH)
    file_path = models.CharField(gettext_lazy("File Path"), max_length=MAX_CHAR_LENGTH, unique=True)
    file_size = models.IntegerField(gettext_lazy("File Size"), default=int)
    extra_params = models.TextField(gettext_lazy("Extra Params"), null=True, blank=True)
    upload_result = models.TextField(gettext_lazy("Upload Result"), null=True, blank=True)
    upload_by = ForeignKey(gettext_lazy("Upload By"), to="account.User", on_delete=models.CASCADE)
    upload_at = models.DateTimeField(gettext_lazy("Upload At"), auto_now_add=True)

    class Meta:
        verbose_name = gettext_lazy("COS Log")
        verbose_name_plural = verbose_name
        ordering = ["-upload_at"]

    @classmethod
    def check_path(cls, file_path: str) -> bool:
        """
        path should uniq
        """

        return not cls.objects.filter(file_path=file_path).exists()
