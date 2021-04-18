class Simulation_Geo_tools:
    @staticmethod
    def Convert_2039_2_4326(feature):
        try:
            #step 1 
            interFeature = feature.to_crs("+proj=tmerc +lat_0=31.7343936111111 +lon_0=35.2045169444445 +k=1.0000067 +x_0=219529.584 +y_0=626907.39 +ellps=GRS80 +towgs84=-23.772,-17.490,-17.859,-0.31320,-1.85274,1.67299,5.4262 +units=m +no_defs")
            crs_4326 =  {'init': 'epsg:4326'}
            #step 2
            Feature_4326 = interFeature.to_crs(crs_4326)
            return (Feature_4326)

        except Exception as e:
            print(e)
        else:
            print("Conversion to WGS 84 Successful")