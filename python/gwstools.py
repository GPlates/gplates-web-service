import requests
import json

base_url = 'http://127.0.0.1:8000'

# fetch reconstructed coastlines
def gws_coastlines(recon_time,model='SETON2012',proxies={'http':''}):

    r = requests.get('%s/reconstruct/coastlines/?time=%0.2f' % (base_url,recon_time),
                     proxies=proxies)
    cs = json.loads(r.text)
    
    return cs

# fetch reconstructed topological plate polygons
def gws_plate_polygons(recon_time,model='SETON2012',proxies={'http':''}):

    r = requests.get('%s/topology/plate_polygons/?time=%0.2f' % (base_url,recon_time),
                     proxies=proxies)
    pp = json.loads(r.text)

    return pp

# fetch reconstructed static polygons
def gws_static_polygons(recon_time,model='SETON2012',proxies={'http':''}):

     r = requests.get('%s/reconstruct/static_polygons/?time=%0.2f' % (base_url,recon_time),
                      proxies=proxies)
     sp = json.loads(r.text)

     return sp

# fetch reconstructed motion paths
def gws_motion_path(recon_time,seedpoints,fixplate,movplate,time_min,time_max,time_step,
                    model='SETON2012',proxies={'http':''}):
    
    r = requests.get('%s/reconstruct/motion_path/?model=%s&time=%0.2f&seedpoints=%s&timespec=%s&fixplate=%d&movplate=%s' % \
                     (base_url,model,recon_time,seedpoints,'%s,%s,%s' % (time_min,time_max,time_step),fixplate,movplate),
                     proxies=proxies)

    motion_path = json.loads(r.text)

    return motion_path

# fetch reconstructed plate velocities
def gws_velocities(recon_time,polygon_type='static',
                   model='SETON2012',velocity_type='MagAzim',proxies={'http':''}):

    if polygon_type=='topology':
        r = requests.get('%s/velocity/plate_polygons/?model=%s&time=%0.2f&velocity_type=%s' % \
                         (base_url,model,recon_time,velocity_type),
                         proxies=proxies)
    else:
        r = requests.get('%s/velocity/static_polygons/?model=%s&time=%0.2f&velocity_type=%s' % \
                         (base_url,model,recon_time,velocity_type),
                         proxies=proxies)

    velocities = json.loads(r.text)

    return velocities
