def get_reconstruction_model_dict(MODEL_NAME):

    
    if MODEL_NAME=='SETON2012':
        
        model_dict = {'RotationFile':'Seton_etal_ESR2012_2012.1.rot',
                      'Coastlines':'Seton_etal_ESR2012_Coastlines_2012.1_Polygon.gpmlz',
                      'StaticPolygons':'Seton_etal_ESR2012_StaticPolygons_2012.1.gpmlz',
                      'PlatePolygons':'Seton_etal_ESR2012_PP_2012.1.gpmlz'}

    elif MODEL_NAME=='MULLER2016':
        model_dict = {'RotationFile':'Seton_etal_ESR2012_2012.1.rot',
                      'Coastlines':'',
                      'StaticPolygons':'',
                      'PlatePolygons':['','']}

    elif MODEL_NAME=='PALEOMAP':
        model_dict = {'RotationFile':'PALEOMAP_PlateModel.rot',
                      'Coastlines':'',
                      'StaticPolygons':''}

    elif MODEL_NAME=='RODINIA2008':
        model_dict = {'RotationFile':'.rot',
                      'Coastlines':'',
                      'StaticPolygons':''}

    else:
        model_dict = 'Error: Model Not Listed'

    return model_dict

