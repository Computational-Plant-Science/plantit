from django.db import models

from job_manager.job import Job
from job_manager.remote import File as JobFile
from file_manager.models import AbstractFile
from workflows.models import AbstractDefaults, Tag
from collection.images import Image

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

class Result(models.Model):
    """
        Represents the results from one root image file.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)

    #Generated with the help of:
    # cat traits.csv | awk -F , '{printf "'\''%s'\'':('\''%s'\'',float),\n ", $1, $1}'
    attributes = {
        'circle ratio': ('CIR_RATIO',float),
        'x pixel':('X_PIXEL',float),
        'y pixel':('Y_PIXEL',float),
        'xScale':('X_SCALE',float),
        'yScale':('Y_SCALE',float),
        'computation time':('COMP_TIME',float),
        'Skeleton Vertices':('SKL_NODES',float),
        'DIA_STM':('DIA_STM',float),
        'DIA_STM_SIMPLE':('DIA_STM_SIMPLE',float),
        'AREA':('AREA',float),
        'AVG_DENSITY':('AVG_DENSITY',float),
        'TD_MED':('TD_MED',float),
        'TD_AVG':('TD_AVG',float),
        'WIDTH_MED':('WIDTH_MED',float),
        'WIDTH_MAX':('WIDTH_MAX',float),
        'D10':('D10',float),
        'D20':('D20',float),
        'D30':('D30',float),
        'D40':('D40',float),
        'D50':('D50',float),
        'D60':('D60',float),
        'D70':('D70',float),
        'D80':('D80',float),
        'D90':('D90',float),
        'DS10':('DS10',float),
        'DS20':('DS20',float),
        'DS30':('DS30',float),
        'DS40':('DS40',float),
        'DS50':('DS50',float),
        'DS60':('DS60',float),
        'DS70':('DS70',float),
        'DS80':('DS80',float),
        'DS90':('DS90',float),
        'RDISTR_X':('RDISTR_X',float),
        'RDISTR_Y':('RDISTR_Y',float),
        'SKL_DEPTH':('SKL_DEPTH',float),
        'SKL_WIDTH':('SKL_WIDTH',float),
        'RTP_COUNT':('RTP_COUNT',float),
        'ANG_TOP':('ANG_TOP',float),
        'ANG_BTM':('ANG_BTM',float),
        'STA_RANGE':('STA_RANGE',float),
        'STA_DOM_I':('STA_DOM_I',float),
        'STA_DOM_II':('STA_DOM_II',float),
        'STA_25_I':('STA_25_I',float),
        'STA_25_II':('STA_25_II',float),
        'STA_50_I':('STA_50_I',float),
        'STA_50_II':('STA_50_II',float),
        'STA_75_I':('STA_75_I',float),
        'STA_75_II':('STA_75_II',float),
        'STA_90_I':('STA_90_I',float),
        'STA_90_II':('STA_90_II',float),
        'RTA_DOM_I':('RTA_DOM_I',float),
        'RTA_DOM_II':('RTA_DOM_II',float),
        'STA_MIN':('STA_MIN',float),
        'STA_MAX':('STA_MAX',float),
        'STA_MED':('STA_MED',float),
        'RTA_RANGE':('RTA_RANGE',float),
        'RTA_MIN':('RTA_MIN',float),
        'RTA_MAX':('RTA_MAX',float),
        'RTA_MED':('RTA_MED',float),
        'NR_RTP_SEG_I':('NR_RTP_SEG_I',float),
        'NR_RTP_SEG_II':('NR_RTP_SEG_II',float),
        'ADVT_COUNT':('ADVT_COUNT',float),
        'BASAL_COUNT':('BASAL_COUNT',float),
        'ADVT_ANG':('ADVT_ANG',float),
        'BASAL_ANG':('BASAL_ANG',float),
        'HYP_DIA':('HYP_DIA',float),
        'TAP_DIA':('TAP_DIA',float),
        'MAX_DIA_90':('MAX_DIA_90',float),
        'DROP_50':('DROP_50',float),
        'CP_DIA25':('CP_DIA25',float),
        'CP_DIA50':('CP_DIA50',float),
        'CP_DIA75':('CP_DIA75',float),
        'CP_DIA90':('CP_DIA90',float),
        'NODAL_LEN':('NODAL_LEN',float),
        'NODAL_AVG_DIA':('NODAL_AVG_DIA',float),
        'LT_BRA_FRQ':('LT_BRA_FRQ',float),
        'LT_AVG_LEN':('LT_AVG_LEN',float),
        'LT_AVG_ANG':('LT_AVG_ANG',float),
        'LT_ANG_RANGE':('LT_ANG_RANGE',float),
        'LT_MIN_ANG':('LT_MIN_ANG',float),
        'LT_MAX_ANG':('LT_MAX_ANG',float),
        'LT_DIST_FIRST':('LT_DIST_FIRST',float),
        'LT_MED_DIA':('LT_MED_DIA',float),
        'LT_AVG_DIA':('LT_AVG_DIA',float),
    }

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
