import requests, json
SERVER_URL = 'http://127.0.0.1:8000/'
proxies = {'http':''}

data={'points':'95,54,142,-33', 'time':140}
r = requests.get(SERVER_URL+'reconstruct/reconstruct_points/', params=data, verify=False, proxies=proxies)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)

r = requests.post(SERVER_URL+'reconstruct/reconstruct_points/',data=data,verify=False, proxies=proxies)
print(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))

data={'points':'95,54,-117.26,32.7,142,-33', 'time':140, 'fc':''}
r = requests.post(SERVER_URL+'reconstruct/reconstruct_points/',data=data,verify=False, proxies=proxies)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)

r = requests.get(SERVER_URL+'reconstruct/reconstruct_points/', params=data, verify=False, proxies=proxies)
#print(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
#print r.text
