from typing import Any, List, Dict
import json
import uuid

def _convert_db_to_api_subsite(db_subsite_in:Dict[str,Any]):
    api_subsite_item = {
        key[10:]:value
        for key,value in db_subsite_in.items()
        if key.startswith("Parameter_")
    }
    api_subsite_item["name"] = db_subsite_in["SubsiteName"]
    return api_subsite_item

def _convert_api_to_db_subsite(
        id_in: str,
        product_in: str,
        sample_in: str,
        site_x_in: str,
        site_y_in: str,
        api_subsite_in: dict):
    db_subsite_item = {
        "id" : id_in,
        "Product" : product_in,
        "Sample" : sample_in,
        "SiteX" : site_x_in,
        "SiteY" : site_y_in,
        "SubsiteName" : api_subsite_in["name"],
        "DataType" : "Subsite",
    }
    # add data fields other than name as parameters
    db_subsite_item.update({
        f"Parameter_{key}":value
        for key,value in api_subsite_in.items()
        if key != "name"
    })
    return db_subsite_item

def _get_subsite_db_item(
        db_table_in,
        product_id_in,
        sample_id_in,
        site_x_in,
        site_y_in,
        subsite_name_in):
    results = db_table_in.scan(
            ExpressionAttributeValues = {
                ":Product":{"S":f"{product_id_in}"},
                ":Sample":f"{sample_id_in}",
                ":SiteX" : f"{site_x_in}",
                ":SiteY" : f"{site_y_in}",
                ":SubsiteName" : f"{subsite_name_in}",
                ":DataType" : "Subsite",
            }
        )    
    return [_convert_db_to_api_subsite(item) for item in results["Items"]]

def _post_subsite_in_db(
        db_table_in,
        product_in: str,
        sample_in: str,
        site_x_in: str,
        site_y_in: str,
        api_subsite_in: Dict) -> Dict:
    db_subsite_data = _convert_api_to_db_subsite(
        str(uuid.uuid4()),
        product_in,
        sample_in,
        site_x_in,
        site_y_in,
        api_subsite_in)
    db_table_in.put_item(Item={"id" : db_subsite_data["id"], "Product" : db_subsite_data["Product"]})
    return f"subsite data succesfully posted with id {db_subsite_data}"


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
    return db_table_in.put_item(Item=site_item)

