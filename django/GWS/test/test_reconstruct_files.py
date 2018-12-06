import requests

#url = 'http://172.16.180.52:18000/reconstruct/reconstruct_files'
url = 'https://gws.gplates.org/reconstruct/reconstruct_files'

files = {
    'file_1': open('Australia_Points.shx', 'rb'),
    'file_2': open('Australia_Points.prj', 'rb'),
    'file_3': open('Australia_Points.shp', 'rb'),
    'file_4': open('Australia_Points.dbf', 'rb')
    }

data = {'time': 100}
r = requests.post(url, files=files, data = data)
open('result.zip', 'wb').write(r.content)
