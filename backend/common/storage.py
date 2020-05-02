import os

from django.core.files.storage import FileSystemStorage

from tsg import settings


class OverwriteStorage(FileSystemStorage):
    """
    Custom Storage which allows to override existing files on the system.

    So if a company uploads a new logo the existing logo will be replaced by the new logo.
    """

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
