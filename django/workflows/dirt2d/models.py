from django.db import models

from job_manager.job import Job
from job_manager.remote import File as JobFile
from workflows.models import AbstractDefaults, Tag
from collection.models import Sample
from django.core import serializers

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
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)

    #Generated using django/workflows/dirt2d/dev/attributes.py
    attributes = {
        'D70':{
            'field': 'D70',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D70'
        },
        'RTP_COUNT':{
            'field': 'RTP_COUNT',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'RTP_COUNT'
        },
        'D10':{
            'field': 'D10',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D10'
        },
        'SKL_DEPTH':{
            'field': 'SKL_DEPTH',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'SKL_DEPTH'
        },
        'D30':{
            'field': 'D30',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D30'
        },
        'DS40':{
            'field': 'DS40',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS40'
        },
        'DS90':{
            'field': 'DS90',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS90'
        },
        'WIDTH_MAX':{
            'field': 'WIDTH_MAX',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'WIDTH_MAX'
        },
        'D50':{
            'field': 'D50',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D50'
        },
        'DS80':{
            'field': 'DS80',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS80'
        },
        'DIA_STM_SIMPLE':{
            'field': 'DIA_STM_SIMPLE',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DIA_STM_SIMPLE'
        },
        'D90':{
            'field': 'D90',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D90'
        },
        'TD_AVG':{
            'field': 'TD_AVG',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'TD_AVG'
        },
        'DS10':{
            'field': 'DS10',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS10'
        },
        'AVG_DENSITY':{
            'field': 'AVG_DENSITY',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'AVG_DENSITY'
        },
        'DS30':{
            'field': 'DS30',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS30'
        },
        'DS60':{
            'field': 'DS60',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS60'
        },
        'SKL_WIDTH':{
            'field': 'SKL_WIDTH',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'SKL_WIDTH'
        },
        'D20':{
            'field': 'D20',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D20'
        },
        'DS70':{
            'field': 'DS70',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS70'
        },
        'DS50':{
            'field': 'DS50',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS50'
        },
        'DIA_STM':{
            'field': 'DIA_STM',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DIA_STM'
        },
        'D40':{
            'field': 'D40',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D40'
        },
        'D60':{
            'field': 'D60',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D60'
        },
        'RDISTR_Y':{
            'field': 'RDISTR_Y',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'RDISTR_Y'
        },
        'RDISTR_X':{
            'field': 'RDISTR_X',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'RDISTR_X'
        },
        'AREA':{
            'field': 'AREA',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'AREA'
        },
        'D80':{
            'field': 'D80',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'D80'
        },
        'TD_MED':{
            'field': 'TD_MED',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'TD_MED'
        },
        'WIDTH_MED':{
            'field': 'WIDTH_MED',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'WIDTH_MED'
        },
        'DS20':{
            'field': 'DS20',
            'type': float,
            'initial': True,
            'description': 'description',
            'group':'Common Traits',
            'name': 'DS20'
        },
        'Skeleton Vertices':{
            'field': 'SKL_NODES',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Computation',
            'name': 'Skeleton Vertices'
        },
        'circle ratio':{
            'field': 'CIR_RATIO',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Computation',
            'name': 'circle ratio'
        },
        'yScale':{
            'field': 'Y_SCALE',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Computation',
            'name': 'yScale'
        },
        'xScale':{
            'field': 'X_SCALE',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Computation',
            'name': 'xScale'
        },
        'computation time':{
            'field': 'COMP_TIME',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Computation',
            'name': 'computation time'
        },
        'x pixel':{
            'field': 'X_PIXEL',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Computation',
            'name': 'x pixel'
        },
        'y pixel':{
            'field': 'Y_PIXEL',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Computation',
            'name': 'y pixel'
        },
        'ADVT_ANG':{
            'field': 'ADVT_ANG',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'ADVT_ANG'
        },
        'CP_DIA25':{
            'field': 'CP_DIA25',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'CP_DIA25'
        },
        'RTA_MED':{
            'field': 'RTA_MED',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'RTA_MED'
        },
        'CP_DIA50':{
            'field': 'CP_DIA50',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'CP_DIA50'
        },
        'STA_MIN':{
            'field': 'STA_MIN',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_MIN'
        },
        'NR_RTP_SEG_I':{
            'field': 'NR_RTP_SEG_I',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'NR_RTP_SEG_I'
        },
        'STA_25_II':{
            'field': 'STA_25_II',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_25_II'
        },
        'STA_MAX':{
            'field': 'STA_MAX',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_MAX'
        },
        'CP_DIA90':{
            'field': 'CP_DIA90',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'CP_DIA90'
        },
        'STA_50_I':{
            'field': 'STA_50_I',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_50_I'
        },
        'BASAL_ANG':{
            'field': 'BASAL_ANG',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'BASAL_ANG'
        },
        'STA_75_II':{
            'field': 'STA_75_II',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_75_II'
        },
        'STA_MED':{
            'field': 'STA_MED',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_MED'
        },
        'RTA_MIN':{
            'field': 'RTA_MIN',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'RTA_MIN'
        },
        'STA_90_II':{
            'field': 'STA_90_II',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_90_II'
        },
        'STA_50_II':{
            'field': 'STA_50_II',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_50_II'
        },
        'RTA_RANGE':{
            'field': 'RTA_RANGE',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'RTA_RANGE'
        },
        'STA_25_I':{
            'field': 'STA_25_I',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_25_I'
        },
        'HYP_DIA':{
            'field': 'HYP_DIA',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'HYP_DIA'
        },
        'STA_DOM_II':{
            'field': 'STA_DOM_II',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_DOM_II'
        },
        'NR_RTP_SEG_II':{
            'field': 'NR_RTP_SEG_II',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'NR_RTP_SEG_II'
        },
        'MAX_DIA_90':{
            'field': 'MAX_DIA_90',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'MAX_DIA_90'
        },
        'BASAL_COUNT':{
            'field': 'BASAL_COUNT',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'BASAL_COUNT'
        },
        'RTA_MAX':{
            'field': 'RTA_MAX',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'RTA_MAX'
        },
        'STA_75_I':{
            'field': 'STA_75_I',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_75_I'
        },
        'RTA_DOM_II':{
            'field': 'RTA_DOM_II',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'RTA_DOM_II'
        },
        'STA_90_I':{
            'field': 'STA_90_I',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_90_I'
        },
        'STA_DOM_I':{
            'field': 'STA_DOM_I',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_DOM_I'
        },
        'CP_DIA75':{
            'field': 'CP_DIA75',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'CP_DIA75'
        },
        'DROP_50':{
            'field': 'DROP_50',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'DROP_50'
        },
        'TAP_DIA':{
            'field': 'TAP_DIA',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'TAP_DIA'
        },
        'ADVT_COUNT':{
            'field': 'ADVT_COUNT',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'ADVT_COUNT'
        },
        'RTA_DOM_I':{
            'field': 'RTA_DOM_I',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'RTA_DOM_I'
        },
        'STA_RANGE':{
            'field': 'STA_RANGE',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Dicot Root Traits',
            'name': 'STA_RANGE'
        },
        'LT_MIN_ANG':{
            'field': 'LT_MIN_ANG',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_MIN_ANG'
        },
        'LT_AVG_ANG':{
            'field': 'LT_AVG_ANG',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_AVG_ANG'
        },
        'NODAL_AVG_DIA':{
            'field': 'NODAL_AVG_DIA',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'NODAL_AVG_DIA'
        },
        'LT_BRA_FRQ':{
            'field': 'LT_BRA_FRQ',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_BRA_FRQ'
        },
        'LT_AVG_LEN':{
            'field': 'LT_AVG_LEN',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_AVG_LEN'
        },
        'LT_DIST_FIRST':{
            'field': 'LT_DIST_FIRST',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_DIST_FIRST'
        },
        'NODAL_LEN':{
            'field': 'NODAL_LEN',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'NODAL_LEN'
        },
        'LT_ANG_RANGE':{
            'field': 'LT_ANG_RANGE',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_ANG_RANGE'
        },
        'LT_MAX_ANG':{
            'field': 'LT_MAX_ANG',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_MAX_ANG'
        },
        'LT_MED_DIA':{
            'field': 'LT_MED_DIA',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_MED_DIA'
        },
        'LT_AVG_DIA':{
            'field': 'LT_AVG_DIA',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Excised Root Traits',
            'name': 'LT_AVG_DIA'
        },
        'ANG_BTM':{
            'field': 'ANG_BTM',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Monocot Root Traits',
            'name': 'ANG_BTM'
        },
        'ANG_TOP':{
            'field': 'ANG_TOP',
            'type': float,
            'initial': False,
            'description': 'description',
            'group':'Monocot Root Traits',
            'name': 'ANG_TOP'
        },
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

    def serialize(self):
        result = {}

        result = serializers.serialize('python',
            [self, ],
            fields = self.attributes.keys() )[0]

        result['name'] = self.sample.name

        return result
