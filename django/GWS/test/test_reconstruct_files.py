import requests

url = 'http://172.16.180.52:18000/reconstruct/reconstruct_files'
files = {
    'file_1': open('Brune_etal_Polygons.shx', 'rb'),
    'file_2': open('Brune_etal_Polygons.sbx', 'rb'),
    'file_3': open('Brune_etal_Polygons.prj', 'rb'),
    'file_4': open('Brune_etal_Polygons.shp', 'rb'),
    'file_5': open('Brune_etal_Polygons.sbn', 'rb'),
    'file_6': open('Brune_etal_Polygons.dbf', 'rb')
    }
r = requests.post(url, files=files)
print(r.text)
