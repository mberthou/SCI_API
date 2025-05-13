from typing import Dict
import json
import uuid
from .site import _post_subsite_in_db, _put_site_db_item

def post_mapping(db_table_in, item_in: str):
    product = item_in["Product"]
    sample = item_in["Sample"]
    mapping_data = item_in["Data"]
    site_x0 = int(item_in["SiteX0"])
    site_y0 = int(item_in["SiteY0"])

    mapping_item = {
        "id" : str(uuid.uuid4()),
        "Product" : product,
        "Sample" : sample,
        "SiteX0" : site_x0,
        "SiteY0" : site_y0,
        "NOSitesX": item_in["NOSitesX"],
        "NOSitesY": item_in["NOSitesY"],
        "SiteWidth": item_in["SiteWidth"],
        "SiteHeight": item_in["SiteHeight"],
    }
    db_table_in.put_item(mapping_item)
    for site_data in mapping_data["Sites"]:
        site_name = site_data["name"]
        site_x = site_x0 + site_data["col"]
        site_y = site_y0 + site_data["row"]
        site_post_result = _put_site_db_item(
            db_table_in, 
            product,
            sample,
            site_x,
            site_y,
            site_name,
            site_data["sel"],
            site_data["NOSubs"])
        for subsite_data in site_data["subsites"]:
            subsite_post_result = _post_subsite_in_db(
                db_table_in, 
                product,
                sample,
                site_x,
                site_y,
                subsite_data)
