import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import folium
import geopandas as gpd


class SimulationPlots:
    @staticmethod
    def get_age_groups():
        age_groups = {
            "age_groups_1": [20, 30, 40, 50, 60, 70, 80, 90, 100],
            "age_percent_1": [26, 18, 13, 12, 11, 9, 6, 4, 1],
            "age_groups_2": [20, 30, 40, 50, 60, 70, 80, 90, 100],
            "age_percent_2": [5, 10, 15, 17.5, 21, 15, 10, 4, 2.5],
            "age_groups_3": [20, 30, 40, 50, 60, 70, 80, 90, 100],
            "age_percent_3": [5, 7.5, 10, 15, 17, 20, 16, 6.5, 3]
        }
        ag = pd.DataFrame.from_dict(age_groups)
        fig = make_subplots(rows=1, cols=3, subplot_titles=(
            "Average Age 44", "Israel distribution Average Age 48", "Average Age 60"))
        fig.add_trace(go.Bar(x=ag['age_groups_1'],
                             y=ag['age_percent_1']), row=1, col=1)
        fig.add_trace(go.Bar(x=ag['age_groups_2'],
                             y=ag['age_percent_2']), row=1, col=2)
        fig.add_trace(go.Bar(x=ag['age_groups_3'],
                             y=ag['age_percent_3']), row=1, col=3)
        fig.update_layout(showlegend=False)
        return fig

    @staticmethod
    def add_multiple_point_layer(points_layer, fmap, layerName):
        # generate the popup message that is shown on click.
        feature_group = folium.FeatureGroup(name=layerName)
        if (layerName == 'Type Project'):
            for i in points_layer.index:
                gpoint = points_layer.loc[i]
                cor = gpoint.XY_array
                operation = gpoint.layer

                tooltip = operation
                popup_text = "<h3>{}</h3></br>"  # 1
                popup_text += "<b>Operation:</b> {} </br>"  # 2
                popup_text += "<b>Plan Number:</b> {} </br>"  # 3
                popup_text += "<b>Total Apt:</b> {}  </br>"  # 4
                popup_text += "<b>Arnona + Vaad:</b> {:,.0f} ₪  </br>"  # 5
                popup_text += "<b>Average Rent:</b> {} ₪ </br>"  # 6
                popup_text += "<b>Area (Mode):</b> {}m\u00b2  </br>"  # 7
                # 8
                popup_text += "<b>Average Seniority:</b> {:.0f} (years) </br>"
                popup_text += "<b>Average Age:</b> {:.0f} (years)  </br>"  # 9
                popup_text += "<b>Percent > 65:</b> {:.0f} %  </br>"  # 10
                popup_text += "<b>Eligble Discount:</b> {:.0%}</br>"  # 11
                popup_text += "<b>Average Discount:</b> {:.0%}</br>"  # 12
                popup_text += "<b>Low Discount:</b> {:.0%}</br>"  # 13
                popup_text += "<b>High Discount:</b> {:.0%}</br>"  # 14

                popup_text = popup_text.format(gpoint.Full_addr_heb,
                                               operation,
                                               gpoint.plan_numbe,
                                               gpoint.TotalApparments,
                                               gpoint.Arnona_Vaad,
                                               gpoint.Average_Rent,
                                               gpoint.AreaMode,
                                               gpoint.avg_living_till_2020,
                                               gpoint.Average_age_2020,
                                               gpoint.percent_above_65,
                                               gpoint.discount_percent,
                                               gpoint.AverageDiscountRate,
                                               gpoint.Low_discount,
                                               gpoint.High_discount)

                tooltip_text = "<b>Hebrew Address:</b> {}<br> <b>Operation:</b> {} <br> <b>Plan Number:</b> {}"
                tooltip_text = tooltip_text.format(
                    gpoint.Full_addr_heb, operation, gpoint.plan_numbe)

                pop = folium.Popup(popup_text, max_width=250)
                tooltip = tooltip_text

                if operation == "Tama38":
                    folium.RegularPolygonMarker(location=cor, color='red', fill=True,
                                                fill_opacity=0.7,
                                                radius=4, number_of_sides=3,
                                                rotation=33.0,
                                                popup=pop,
                                                tooltip=tooltip).add_to(feature_group)

                elif operation == "Tama38_2":
                    folium.RegularPolygonMarker(location=cor, color='blue', fill=True,
                                                fill_opacity=0.7,
                                                radius=4, number_of_sides=4,
                                                rotation=33.0,
                                                popup=pop,
                                                tooltip=tooltip).add_to(feature_group)
                else:
                    folium.CircleMarker(location=cor, color='yellow', fill=True, radius=4, fill_opacity=0.7,
                                        popup=pop, tooltip=tooltip
                                        ).add_to(feature_group)
        else:
            folium.Marker([32.02600, 34.74202],
                          popup='<strong>Location1</strong>', tooltip=tooltip,
                          icon=folium.Icon(color='purple', icon='cloud')).add_to(feature_group)

        feature_group.add_to(fmap)
        return fmap

    # creates a map of Bat Yam with the background buildings
    @staticmethod
    def createNewMap(lat=32.02677, lon=34.74283):
        # initate map
        latlng = [lat, lon]
        zoom = 20
        f = folium.Figure(width=1000, height=1000)
        fmap = folium.Map(latlng, zoom_start=zoom,
                          tiles='cartodbpositron').add_to(f)

        return(fmap)

    @staticmethod
    def add_poly_layer(layer_wgs_84, layerName, colorRGB, fl, al, fmap):
        gjson = layer_wgs_84.to_json()
        if (layerName == 'Statistical'):
            # Statistical Borders
            feature_group = folium.FeatureGroup(name=layerName)
            style = {'fillOpacity': 0.0, 'weight': 2,
                     'fillColor': colorRGB, 'dashArray': '10, 10'}
            folium.GeoJson(gjson, style_function=lambda x: style).add_to(
                feature_group)

        elif (layerName == 'Background Buildings'):
            # Buildings Background
            feature_group = folium.FeatureGroup(name=layerName)
            style = {'fillOpacity': 0.8, 'weight': 0, 'fillColor': colorRGB}
            folium.GeoJson(gjson, style_function=lambda x: style).add_to(
                feature_group)

        elif (layerName == 'Future Plan'):
            # Polygon Future Plans
            feature_group = folium.FeatureGroup(name=layerName)
            style = {'fillOpacity': 0.25, 'weight': 0, 'fillColor': colorRGB}
            folium.GeoJson(gjson, style_function=lambda x: style,
                           tooltip=folium.GeoJsonTooltip(fields=fl,
                                                         aliases=al)
                           ).add_to(feature_group)
        elif (layerName == 'Future Buildings'):
            # Future Buildings Polygon
            feature_group = folium.FeatureGroup(name=layerName)
            style = {'fillOpacity': 0.5, 'weight': 1,
                     'color': colorRGB, 'fillColor': colorRGB}
            fl = ['Hebrew Address', 'operation', 'FuturePlanID',
                  'TotalUnits', 'floors', 'Monthly_Mortgage', 'Average_Rent']
            al = ['Hebrew Address: ', 'Operation: ', 'Plan ID: ', 'Total Apt: ', 'Floors: ', 'Average Mortgage: ',
                  'Average Rent: ']
            tooltip = folium.GeoJsonTooltip(fields=fl, aliases=al)
            geojson = folium.GeoJson(gjson, style_function=lambda x: style,
                                     tooltip=folium.GeoJsonTooltip(fields=fl,
                                                                   aliases=al)
                                     )
            geojson.add_to(feature_group)

        feature_group.add_to(fmap)
        return fmap

    def save_map(simulation_report_path, spw_filter, exe_1, pb_31_wgs, btu_wgs, st_84, bld_84, saveMap=True):
        lat = spw_filter[spw_filter['exe_order'] ==
                         exe_1[-1]].geometry.centroid.y.values[0]
        lng = spw_filter[spw_filter['exe_order'] ==
                         exe_1[-1]].geometry.centroid.x.values[0]
        points_subset = gpd.sjoin(
            pb_31_wgs, spw_filter, how='inner', op='intersects', lsuffix='')[pb_31_wgs.columns]
        btu_wgs_subset = gpd.sjoin(
            btu_wgs, spw_filter, how='inner', op='intersects', lsuffix='')
        btu_wgs_subset.rename(
            columns={'key_': 'key', 'operation_': 'operation'}, inplace=True)
        fmap = SimulationPlots.createNewMap(lat, lng)
        fmap = SimulationPlots.add_poly_layer(
            st_84, 'Statistical', '', [''], [''], fmap)
        fmap = SimulationPlots.add_poly_layer(
            bld_84, 'Background Buildings', '#878787', [''], [''], fmap)
        fmap = SimulationPlots.add_poly_layer(spw_filter, 'Future Plan', '#ffb400', [
                                              'plan_number', 'operation'], ['plan number:', 'Operation'], fmap)
        fmap = SimulationPlots.add_poly_layer(
            btu_wgs_subset, 'Future Buildings', '#fc0303', [], [], fmap)

        fmap = SimulationPlots.add_multiple_point_layer(
            points_subset, fmap, 'Type Project')

        folium.LayerControl().add_to(fmap)
        if saveMap == True:
            fmap.save(simulation_report_path+"map.html")
        return fmap
