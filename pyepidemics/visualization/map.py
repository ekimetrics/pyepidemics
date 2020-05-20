import json
import pydeck as pdk

def open_geojson_file(filepath):
    return json.loads(open(filepath,"r").read())


LAT_FRANCE = 46.978926
LNG_FRANCE = 2.736006


def show_geojson_pydeck_choropleth(geojson_data,longitude = LNG_FRANCE,latitude = LAT_FRANCE,zoom = 4,return_object = False):
    """Show geojson using pydeck
    Can be used in streamlit application

    Documentation: 
        https://deckgl.readthedocs.io/en/stable/layer.html#example-vancouver-property-values

    Args:
        geojson_data (dict): GeoJson input file or str to display
        longitude (float, optional): Center longitude. Defaults to France Longitude.
        latitude (float, optional): Center latitude. Defaults to France Latitude.
        zoom (int, optional): Initial zoom. Defaults to 4.
        return_object (bool, optional): Returns pydeck object for streamlit. Defaults to False.

    Returns:
        pydeck object: PyDeck object to visualize in streamlit
    """

    if isinstance(geojson_data,str):
        geojson_data = open_geojson_file(geojson_data)

        # get_fill_color='[255, properties.color * 255/2, 0]',

    geojson = pdk.Layer(
        'GeoJsonLayer',
        geojson_data,
        opacity=0.5,
        stroked=True,
        filled=True,
        extruded=True,
        wireframe=True,
        get_fill_color="properties.color",
        get_line_color=[0,0,0],
        pickable=True
    )

    # Set the viewport location
    view_state = pdk.ViewState(
        map_style='mapbox://styles/mapbox/light-v9',    
        longitude=longitude,
        latitude=latitude,
        zoom=zoom,
        min_zoom=5,
        max_zoom=15,
    )

    # Render
    r = pdk.Deck(layers=[geojson], initial_view_state=view_state)

    if not return_object:
        return r.to_html()
    else:
        return r