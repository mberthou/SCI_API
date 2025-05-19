from typing import Any, List, Dict
import json
import uuid
from .subsite import _post_subsite_in_db, __get_db_subsites_items, _convert_db_to_api_subsite
from decimal import Decimal

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

def __convert_db_site_to_api(db_site_item:Dict, db_subsite_items: List[Dict]):
    db_site_data = json.loads(db_site_item["Data"],parse_float=Decimal)
    api_subsites = [_convert_db_to_api_subsite(db_subsite) for db_subsite in db_subsite_items]
    return {
        "name" : db_site_item["Name"],
        "sel" : db_site_item["IsSelected"],
        "NOSubs" : db_site_data["NOSubs"],
        "subsites" : api_subsites
    }

def __get_db_site_item(
        db_table_in,
        product_id_in: str,
        sample_id_in: str,
        site_x_in: int,
        site_y_in: int):
    results = db_table_in.scan(
            ExpressionAttributeValues = {
                ":Product":{"S":f"{product_id_in}"},
                ":Sample":f"{sample_id_in}",
                ":SiteX" : f"{site_x_in}",
                ":SiteY" : f"{site_y_in}",
                ":DataType" : "Site",
            }
        )
    
    if not results["Items"]:
        raise RuntimeError(f"failed to find Site at coordinates ({site_x_in},{site_y_in})")

    return results["Items"][0]


def _get_api_site_from_db(
        db_table_in,
        product_in: str,
        sample_in: str,
        site_x_in: int,
        site_y_in: int):
    db_site = __get_db_site_item(
        db_table_in,
        product_in,
        sample_in,
        site_x_in,
        site_y_in
    )

    db_subsites = __get_db_subsites_items(
        db_table_in,
        product_in,
        sample_in,
        site_x_in,
        site_y_in
    )

    __convert_db_site_to_api(db_site,db_subsites)



