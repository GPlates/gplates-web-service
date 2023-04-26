def get_lats_lons(params):
    '''
    return two lists, one is the lats and the other is lons
    '''
    points_str = params.get("points", None)
    lats_str = params.get("lats", None)
    lons_str = params.get("lons", None)
    lats = []
    lons = []
    if points_str:
        # filter out invalid characters
        # points_str = "".join(c for c in points_str if c.isdecimal()
        #                     or (c in [".", ",", "-"]))
        ps = points_str.split(",")
        ps_len = len(ps)
        if ps_len > 0 and ps_len % 2 == 0:
            lats = ps[1::2]
            lons = ps[0::2]
        else:
            raise Exception(
                f"Invalid 'points' parameter. The longitude and latitude should come in pairs ({points_str})."
            )
    else:
        if lats_str and lons_str:
            lats = lats_str.split(",")
            lons = lons_str.split(",")
            if len(lats) != len(lons):
                raise Exception(
                    f"Invalid 'lats' and 'lons' parameter. ({lats_str}), ({lons_str})."
                )
    if lats and lons:
        try:
            lats = [float(i) for i in lats]
            lons = [float(i) for i in lons]
        except:
            raise Exception(
                f"Invalid coordinates. ({lats_str}), ({lons_str})."
            )
    return lats, lons
