from uk_covid19 import Cov19API

filt = [
    f'areaName=Exeter',
    f'areaType=ltla'
    ]


struc = {
    "areaName": "areaName",
    "areaType": "areaType",
    "date": "date",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    }



print(Cov19API(filters=filt, structure=struc))


