import csv

from job_manager.job import Task,Status
from job_manager.remote import SSHTaskMixin

from .models import Results

class DownloadResultsTask(SSHTaskMixin,Task):
    """
        Downloads and parsers the csv output by the DIRT algorithm. Populating
        RootImage objects with the resutls from each analyzed image.
    """

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

    def parse_csv_file(self,file):
        """
            Extracts the results from the csv file and inserts into the
            cooresponding RootImage object using attributs for field
            mapping and value formatting.
        """
        reader = csv.DictReader(file, delimiter=',',restval=None)
        collection = self.job.rootcollection_set.only()[0]
        for i,row in enumerate(reader):
            if(i%2 == 0):#Skip the rows that are file headers
                try:
                    image = collection.images.get(name=row['Image name'])
                except RootImage.DoesNotExist as e:
                    #TODO: Report this error to the job
                    continue

                for key, value in row.items():
                    if key in self.attributes:
                        attr = self.attributes[key][0]
                        func = self.attributes[key][1]
                        setattr(image,
                                attr,
                                func(value))
                image.save()

    def ssh(self):
        print("here")
        output_file = self.workdir + "/calculated_traits.csv"

        file = self.sftp.file(output_file)
        print("Got File" + str(file))

        self.parse_csv_file(file)

        #Cleanup
        self.finish()
