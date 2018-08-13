from django.db import models

from job_manager.remote import File as JobFile
from file_manager.models import AbstractFile
from workflows.models import AbstractDefaults, Tag, AbstractMetaData, AbstractCollection

"""
    Workflow for the DIRT2D code.
"""

class Defaults(AbstractDefaults):
    """
        Default Collection/Job Values

        Contains the default submission_script, files, and paramaters required
        to create a :class:`job_manager.contrib.SubmissionTask`.

        Attributes:
            submission_script (ForeignKey): the :class:`job_manager.contrib.File`
                that is run by the cluster as {sub_script}
                (see :class:`job_manager.models.Cluster`) upon submissionself.
            files (ManyToMany): Supporting :class:`job_manager.contrib.File`
                that are also copied to the cluster on submission
            parameters (TextField): parameters passed to the submission_script
    """
    submission_script = models.ForeignKey(JobFile,
                                        blank=True,
                                        null=True,
                                        on_delete=models.SET_NULL,
                                        related_name="submission_script")
    files = models.ManyToManyField(JobFile,blank=True)
    parameters = models.TextField(null=True,blank=True)

class MetaData(AbstractMetaData):
    """
        Metadata

        Attributes:
            key (str): Metadata key
            value (str): Metadata value
    """
    pass

class RootImage(AbstractFile):
    """
        Represents one root image file.

        Attributes:
            path (str): the path to the file
            name (str): name of the file
            metadata (ManyToManyField): User configurable metadata
    """
    metadata = models.ManyToManyField(MetaData,blank=True)

    EXP_CODE = models.FloatField(blank=True,null=True)
    CIR_RATIO = models.FloatField(blank=True,null=True)
    X_PIXEL = models.FloatField(blank=True,null=True)
    Y_PIXEL = models.FloatField(blank=True,null=True)
    X_SCALE = models.FloatField(blank=True,null=True)
    Y_SCALE = models.FloatField(blank=True,null=True)
    COMP_TIME = models.FloatField(blank=True,null=True)
    SKL_NODES = models.FloatField(blank=True,null=True)
    DIA_STM = models.FloatField(blank=True,null=True)
    DIA_STM_SIMPLE = models.FloatField(blank=True,null=True)
    AREA = models.FloatField(blank=True,null=True)
    AVG_DENSITY = models.FloatField(blank=True,null=True)
    TD_MED = models.FloatField(blank=True,null=True)
    TD_AVG = models.FloatField(blank=True,null=True)
    WIDTH_MED = models.FloatField(blank=True,null=True)
    WIDTH_MAX = models.FloatField(blank=True,null=True)
    D10 = models.FloatField(blank=True,null=True)
    D20 = models.FloatField(blank=True,null=True)
    D30 = models.FloatField(blank=True,null=True)
    D40 = models.FloatField(blank=True,null=True)
    D50 = models.FloatField(blank=True,null=True)
    D60 = models.FloatField(blank=True,null=True)
    D70 = models.FloatField(blank=True,null=True)
    D80 = models.FloatField(blank=True,null=True)
    D90 = models.FloatField(blank=True,null=True)
    DS10 = models.FloatField(blank=True,null=True)
    DS20 = models.FloatField(blank=True,null=True)
    DS30 = models.FloatField(blank=True,null=True)
    DS40 = models.FloatField(blank=True,null=True)
    DS50 = models.FloatField(blank=True,null=True)
    DS60 = models.FloatField(blank=True,null=True)
    DS70 = models.FloatField(blank=True,null=True)
    DS80 = models.FloatField(blank=True,null=True)
    DS90 = models.FloatField(blank=True,null=True)
    RDISTR_X = models.FloatField(blank=True,null=True)
    RDISTR_Y = models.FloatField(blank=True,null=True)
    SKL_DEPTH = models.FloatField(blank=True,null=True)
    SKL_WIDTH = models.FloatField(blank=True,null=True)
    RTP_COUNT = models.FloatField(blank=True,null=True)
    ANG_TOP = models.FloatField(blank=True,null=True)
    ANG_BTM = models.FloatField(blank=True,null=True)
    STA_RANGE = models.FloatField(blank=True,null=True)
    STA_DOM_I = models.FloatField(blank=True,null=True)
    STA_DOM_II = models.FloatField(blank=True,null=True)
    STA_25_I = models.FloatField(blank=True,null=True)
    STA_25_II = models.FloatField(blank=True,null=True)
    STA_50_I = models.FloatField(blank=True,null=True)
    STA_50_II = models.FloatField(blank=True,null=True)
    STA_75_I = models.FloatField(blank=True,null=True)
    STA_75_II = models.FloatField(blank=True,null=True)
    STA_90_I = models.FloatField(blank=True,null=True)
    STA_90_II = models.FloatField(blank=True,null=True)
    RTA_DOM_I = models.FloatField(blank=True,null=True)
    RTA_DOM_II = models.FloatField(blank=True,null=True)
    STA_MIN = models.FloatField(blank=True,null=True)
    STA_MAX = models.FloatField(blank=True,null=True)
    STA_MED = models.FloatField(blank=True,null=True)
    RTA_RANGE = models.FloatField(blank=True,null=True)
    RTA_MIN = models.FloatField(blank=True,null=True)
    RTA_MAX = models.FloatField(blank=True,null=True)
    RTA_MED = models.FloatField(blank=True,null=True)
    NR_RTP_SEG_I = models.FloatField(blank=True,null=True)
    NR_RTP_SEG_II = models.FloatField(blank=True,null=True)
    ADVT_COUNT = models.FloatField(blank=True,null=True)
    BASAL_COUNT = models.FloatField(blank=True,null=True)
    BASAL_ANG = models.FloatField(blank=True,null=True)
    ADVT_ANG = models.FloatField(blank=True,null=True)
    HYP_DIA = models.FloatField(blank=True,null=True)
    TAP_DIA = models.FloatField(blank=True,null=True)
    MAX_DIA_90 = models.FloatField(blank=True,null=True)
    DROP_50 = models.FloatField(blank=True,null=True)
    CP_DIA25 = models.FloatField(blank=True,null=True)
    CP_DIA50 = models.FloatField(blank=True,null=True)
    CP_DIA75 = models.FloatField(blank=True,null=True)
    CP_DIA90 = models.FloatField(blank=True,null=True)
    NODAL_LEN = models.FloatField(blank=True,null=True)
    NODAL_AVG_DIA = models.FloatField(blank=True,null=True)
    LT_BRA_FRQ = models.FloatField(blank=True,null=True)
    LT_AVG_LEN = models.FloatField(blank=True,null=True)
    LT_AVG_ANG = models.FloatField(blank=True,null=True)
    LT_ANG_RANGE = models.FloatField(blank=True,null=True)
    LT_MIN_ANG = models.FloatField(blank=True,null=True)
    LT_MAX_ANG = models.FloatField(blank=True,null=True)
    LT_DIST_FIRST = models.FloatField(blank=True,null=True)
    LT_MED_DIA = models.FloatField(blank=True,null=True)
    LT_AVG_DIA = models.FloatField(blank=True,null=True)


class RootCollection(AbstractCollection):
    """
        Contains a collection of root images that are analyzed togeather.
        Typically representing one experiment or treatment

        Attributes:
            name (str): the name of the collection
            description (str): text description
            user (ForeignKey): primary user for the collection
            images (ManyToMany): root images (:class:`.models.RootImage`) within
                the collection
            metadata (ForeignKey): User configurable metadata
                (:class:`.models.MetaData`)
    """
    images = models.ManyToManyField(RootImage,blank=True)
    metadata = models.ManyToManyField(MetaData,blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/workflows/dirt2d/collection/%d/details"%(self.pk,)
