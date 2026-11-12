from django.conf import settings
from django.core.files.storage import default_storage


def video_storage():
    """视频文件的存储：线上用 Cloudinary 的视频存储，本地用默认存储。"""
    if getattr(settings, "USE_CLOUDINARY", False):
        from cloudinary_storage.storage import VideoMediaCloudinaryStorage

        return VideoMediaCloudinaryStorage()
    return default_storage
