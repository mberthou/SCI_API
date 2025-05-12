from typing import Dict
import json
import uuid

def _post_subsite_db_item(
        db_table_in,
        product_in,
        sample_in,
        site_x_in,
        site_y_in,
        subsite_data_in: Dict) -> Dict:
    subsite_item = {
        "id" : str(uuid.uuid4()),
        "Product" : product_in,
        "Sample" : sample_in,
        "SiteX" : site_x_in,
        "SiteY" : site_y_in,
        "SubSiteName" : subsite_data_in["name"],
        "DataType" : "Subsite",
    }
    for (key,value) in subsite_data_in:
        if key is not "name":
            subsite_item[f"Parameter_{key}"] = value
    
    return db_table_in.put_item(subsite_item)


def _put_site_db_item(db_table_in, product_in, sample_in, site_x_in, site_y_in, site_name_in, selected_in, no_subs_in):
    site_item = {
        "id" : str(uuid.uuid4()),
        "Product" : product_in,
        "Sample" : sample_in,
        "SiteX" : site_x_in,
        "SiteY" : site_y_in,
        "SiteName" : site_name_in,
        "DataType" : "Site",
        "Selected" : selected_in,
        "Data" : json.dumps({
            "NOSubs" : no_subs_in,
        })
    }
    return db_table_in.put_item(site_item)



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
            subsite_post_result = _post_subsite_db_item(
                db_table_in, 
                product,
                sample,
                site_x,
                site_y,
                subsite_data)
