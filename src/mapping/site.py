from typing import Any, List, Dict
import json
import uuid
from src.Encoders.dynamodb_encoder import DynamoDBEncoder

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
        site_x_in: int,
        site_y_in: int,
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
        site_x_in: int,
        site_y_in: int,
        api_subsite_in: Dict) -> Dict:
    db_subsite_data = _convert_api_to_db_subsite(
        str(uuid.uuid4()),
        product_in,
        sample_in,
        site_x_in,
        site_y_in,
        api_subsite_in)
    db_table_in.put_item(Item=db_subsite_data)
    return f"subsite data succesfully posted with id {db_subsite_data}"

""" posting site and subsites data in db

site posted with structure as follow:
id : str
Product : str
Sample : str
SiteX : str
SiteY : str
DataType: "Site"
IsSelected: bool
Data : {"NoSubs" : int }

subsites data posted in different rows, see _post_subsite_in_db
"""
def _post_api_site_to_db(
        db_table_in,
        product_in: str,
        sample_in: str,
        site_x0_in: int,
        site_y0_in: int,
        row: int,
        col: int,
        site_data_in: Dict):
    site_x = site_x0_in + col
    site_y = site_y0_in + row
    site_item = {
        "id" : str(uuid.uuid4()),
        "Product" : product_in,
        "Sample" : sample_in,
        "SiteX" : site_x,
        "SiteY" : site_y,
        "DataType" : "Site",
        "Name" : site_data_in["name"],
        "IsSelected" : site_data_in["sel"] if "sel" in site_data_in else False,
        "Data" : json.dumps({
            "NOSubs" : site_data_in["NOSubs"],
        })
    }
    db_table_in.put_item(Item=site_item)

    for subsite_data in site_data_in["subsites"]:
        _post_subsite_in_db(
            db_table_in, 
            product_in,
            sample_in,
            site_x,
            site_y,
            subsite_data)

