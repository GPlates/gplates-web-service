import os
from django.conf import settings

def get_reconstruction_model_dict(MODEL_NAME):
    # Model registry - really should not be in here, TODO move to separate registry file

    if MODEL_NAME=='SETON2012':
        model_dict = {'RotationFile':['Seton_etal_ESR2012_2012.1.rot'],
                      'Coastlines':'coastlines_low_res/Seton_etal_ESR2012_Coastlines_2012.shp',
                      'StaticPolygons':'Seton_etal_ESR2012_StaticPolygons_2012.1.gpmlz',
                      'PlatePolygons':['Seton_etal_ESR2012_PP_2012.1.gpmlz'],
                      'ValidTimeRange':[200.,0.]}

    elif MODEL_NAME=='MULLER2016':
        model_dict = {'RotationFile':['Global_EarthByte_230-0Ma_GK07_AREPS.rot'],
                      'Coastlines':'Global_EarthByte_230-0Ma_GK07_AREPS_Coastlines.gpmlz',
                      'StaticPolygons':'Global_EarthByte_GPlates_PresentDay_StaticPlatePolygons_2015_v1.gpmlz',
                      'PlatePolygons':['Global_EarthByte_230-0Ma_GK07_AREPS_PlateBoundaries.gpmlz',
                                       'Global_EarthByte_230-0Ma_GK07_AREPS_Topology_BuildingBlocks.gpmlz'],
                      'ValidTimeRange':[230.,0.]}

    elif MODEL_NAME=='PALEOMAP':
        model_dict = {'RotationFile':['PALEOMAP_PlateModel.rot'],
                      'Coastlines':'PALEOMAP_coastlines.gpmlz',
                      'StaticPolygons':'PALEOMAP_PlatePolygons.gpmlz',
                      'ValidTimeRange':[750.,0.]}

    elif MODEL_NAME=='RODINIA2013':
        model_dict = {'RotationFile':['Li_Rodinia_v2013.rot'],
                      'Coastlines':'Li_Rodinia_v2013_Coastlines.gpmlz',
                      'StaticPolygons':'Li_Rodinia_v2013_StaticPolygons.gpmlz',
                      'ValidTimeRange':[1100.,530.]}

    elif MODEL_NAME=='GOLONKA':
        model_dict = {'RotationFile':['Phanerozoic_EarthByte.rot'],
                      'Coastlines':'Phanerozoic_EarthByte_Coastlines.gpmlz',
                      'StaticPolygons':'Phanerozoic_EarthByte_ContinentalRegions.gpmlz',
                      'ValidTimeRange':[540.,0.]}

    elif MODEL_NAME=='VH_VDM':
        model_dict = {'RotationFile':['vanHinsbergen_master.rot'],
                      'Coastlines':'Coastlines_Seton_etal_2012.gpmlz',
                      'StaticPolygons':'Basis_Polygons_Seton_etal_2012.gpmlz',
                      'ValidTimeRange':[200.,0.]}

    elif MODEL_NAME in ['MATTHEWS2016', 'MATTHEWS2016_mantle_ref']:
        model_dict = {'RotationFile':['Global_EB_250-0Ma_GK07_Matthews_etal.rot',
                                      'Global_EB_410-250Ma_GK07_Matthews_etal.rot'],
                      'Coastlines':'Global_coastlines_2015_v1_low_res.gpmlz',
                      'StaticPolygons':'PresentDay_StaticPlatePolygons_Matthews++.gpmlz',
                      'PlatePolygons':['Global_EarthByte_Mesozoic-Cenozoic_plate_boundaries_Matthews_etal.gpmlz',
                                       'Global_EarthByte_Paleozoic_plate_boundaries_Matthews_etal.gpmlz',
                                       'TopologyBuildingBlocks_AREPS.gpmlz'],
                      'ValidTimeRange':[410.,0.]}
    elif MODEL_NAME == 'MATTHEWS2016_pmag_ref':
        model_dict = {
            "PlatePolygons": [
                    "Matthews_etal_GPC_2016_Paleozoic_PlateTopologies.gpmlz",
                    "Matthews_etal_GPC_2016_MesozoicCenozoic_PlateTopologies.gpmlz"],
            "RotationFile": [
                    "Matthews_etal_GPC_2016_410-0Ma_GK07.rot"],
            "Coastlines": "Matthews_etal_GPC_2016_Coastlines.gpmlz",
            "ValidTimeRange": [
                    410.0,
                    0.0],
            "StaticPolygons": "Muller_etal_AREPS_2016_StaticPolygons.gpmlz"}

    elif MODEL_NAME=='DOMEIER2014':
        model_dict = {'RotationFile':['LP_TPW.rot'],
                      'Coastlines':'LP_land.shp',
                      'StaticPolygons':'LP_land.shp',
                      'PlatePolygons':['LP_ridge.gpml',
                                       'LP_subduction.gpml',
                                       'LP_transform.gpml',
                                       'LP_topos.gpml'],
                      'ValidTimeRange':[410.,250.]}

    elif MODEL_NAME=='PEHRSSON2015':
        model_dict = {'RotationFile':['T_Rot_Model_Abs_25Ma_20131004.rot'],
                      'Coastlines':'PlatePolygons.shp',
                      'StaticPolygons':'PlatePolygons.shp',
                      'ValidTimeRange':[2100.,1275.]}

    else:
        #model_dict = 'Error: Model Not Listed'
        model_dict = None

    return model_dict


def get_model_name_list(MODEL_STORE,include_hidden=True):
    # get a list of models from the model store.
    # if 'include_hidden' is set to False, only the manually defined list of 'validated'
    # models is returned. Otherwise, assume every directory within the model store is a valid model

    if include_hidden:
        MODEL_LIST = [o for o in os.listdir(MODEL_STORE) if os.path.isdir(os.path.join(MODEL_STORE,o))]
    else:
        MODEL_LIST = ['SETON2012','MULLER2016','PALEOMAP','GOLONKA','RODINIA2013',
            'DOMEIER2014','MATTHEWS2016_mantle_ref', 'MATTHEWS2016', 'MATTHEWS2016_pmag_ref']

    return MODEL_LIST


def get_model_dictionary(MODEL_STORE):
    # NOT WORKING YET
    MODEL_LIST = [o for o in os.listdir(MODEL_STORE) if os.path.isdir(os.path.join(MODEL_STORE,o))]

    for MODEL in MODEL_LIST:
        model_dict = get_reconstruction_model_dict(MODEL)
        models_dict[MODEL] = model_dict

    return MODEL_LIST


def is_time_valid_model(model_dict,time):
    # returns True if the time is within the valid time of specified model
    return float(time)<=model_dict['ValidTimeRange'][0] and float(time)>=model_dict['ValidTimeRange'][1]



