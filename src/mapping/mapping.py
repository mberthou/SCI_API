from typing import Dict
import json
import uuid
from .site import _post_subsite_in_db, _post_api_site_to_db

def post_mapping(db_table_in, item_in: str):
    product = item_in["Product"]
    sample = item_in["Sample"]
    mapping_data = item_in["Data"]
    site_x0 = int(mapping_data["SiteX0"])
    site_y0 = int(mapping_data["SiteY0"])

    mapping_item = {
        "id" : str(uuid.uuid4()),
        "Product" : product,
        "Sample" : sample,
        "SiteX0" : site_x0,
        "SiteY0" : site_y0,
        "NOSitesX": mapping_data["NOSitesX"],
        "NOSitesY": mapping_data["NOSitesY"],
        "SiteWidth": mapping_data["SiteWidth"],
        "SiteHeight": mapping_data["SiteHeight"],
    }
    db_table_in.put_item(mapping_item)
    for site_data in mapping_data["sites"]:
        _post_api_site_to_db(
            db_table_in, 
            product,
            sample,
            site_x0,
            site_y0,
            site_data)
