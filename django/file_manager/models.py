from django.db import models

class AbstractFile(models.Model):
    """
        Represents one file.

        Fields:
            : path : the path to the file
            : name : name of the file
            : metadata : User configurable metadata
    """
    path = models.CharField(max_length=250, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
