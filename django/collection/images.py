from os import path

from django.db import models
from collection.models import Collection
from file_manager.models import AbstractFile
from .models import MetaData
from file_manager.filesystems.storage import AbstractStorageType

class Image(AbstractFile):
    pass

class Images2D(Collection):
    files = models.ManyToManyField(Image)

    def add_file(self,file):
        image, _ = Image.objects.get_or_create(path=file,
                     storage=AbstractStorageType.objects.get(name=self.storage_type),
                     name=path.basename(file))
        self.files.add(image)
