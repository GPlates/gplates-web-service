
# coding: utf-8

# In[1]:


import requests, json
SERVER_URL = 'http://localhost:80/'
proxies = {'http':''}


# In[2]:



data={'points':'95,54,142,-33', 'time':140}
r = requests.get(SERVER_URL+'reconstruct/reconstruct_points/', params=data, verify=False, proxies=proxies)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)

r = requests.post(SERVER_URL+'reconstruct/reconstruct_points/',data=data,verify=False, proxies=proxies)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)

data={'points':'95,54,-117.26,32.7,142,-33', 'time':140, 'fc':''}
r = requests.post(SERVER_URL+'reconstruct/reconstruct_points/',data=data,verify=False, proxies=proxies)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)

r = requests.get(SERVER_URL+'reconstruct/reconstruct_points/', params=data, verify=False, proxies=proxies)
print(json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4))
#print r.text


# In[3]:



data= {
   'feature_collection' :
       '''{"type":"FeatureCollection",
           "features":[
               {"type":"Feature",
               "geometry":{
                   "type":"Polygon",
                   "coordinates":[[[128,-17],[133,-18],[138,-19],
                       [140,-23],[139,-27],[130,-27],[128,-24],
                       [127,-21],[127,-17],[128,-17]]]},
                   "properties":{
                       "id":123,
                       "waht":"345"
                   }},
                   
                   {"type":"Feature",
                   "geometry":
                   {
                       "type":"Point",
                       "coordinates":[51.0, 38.0]
                   },
                   "properties":{
                       "id":222
                   }
                   }
           
                   
                   ]}
       ''',
   'geologicage':'140',
   'model':'SETON2012',
   
}

print(data)

r = requests.get(SERVER_URL+'reconstruct/reconstruct_feature_collection/', params=data, verify=False, proxies=proxies)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)

data['keep_properties'] = ''
r = requests.get(SERVER_URL+'reconstruct/reconstruct_feature_collection/', params=data, verify=False, proxies=proxies)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)

r = requests.post(SERVER_URL+'reconstruct/reconstruct_feature_collection/', data=data, verify=False, proxies=proxies)
print(r.text)
#print json.dumps(json.loads(str(r.text)), sort_keys=True, indent=4)


# In[16]:


r = requests.get('http://paleobiodb.org/data1.1/occs/list.json?limit=all&interval_id=3001&show=coords,attr,loc,prot,time,strat,stratext,lith,lithext,geo,rem,ent,entname,crmod&showsource',
                 proxies=proxies)

print(r.status_code)
print(r.headers['content-type'])
print(r.encoding)

pbdb = json.loads(r.text)

lons = []
lats = []
for record in pbdb['records']:
    lons.append(record['lng'])
    lats.append(record['lat'])

print(pbdb)


# In[4]:


fc = {"type": "FeatureCollection"}
fc["features"] = []
for i,record in enumerate(pbdb['records']):
    feature = {"type": "Feature"}
    feature["geometry"] = {}
    feature["geometry"]["type"] = "Point"
    feature["geometry"]["coordinates"] = [record['lng'],record['lat']]
    feature["properties"] = {}
    feature["properties"]['Id'] = 'tmp'
    fc["features"].append(feature)


data= {'feature_collection' : json.dumps(fc)}

data['keep_properties'] = ''
data['time'] = 120.

#print data

r = requests.post(SERVER_URL+'reconstruct/reconstruct_feature_collection/', data=data, verify=False, proxies=proxies)
#print r.text

pts = json.loads(r.text)

#print pts

for feature in pts['features']:
    coords = feature['geometry']['coordinates']
    print(coords)

