from typing import Any, List, Dict
import json
from xml.dom.minidom import Attr
from .subsite import _post_subsite_in_db, __get_db_subsites_items, _convert_db_to_api_subsite
from decimal import Decimal
from boto3.dynamodb.conditions import And, Attr, Key
from functools import reduce
import re
import uuid
import copy

""" posting site and subsites data in db

site posted with structure as follow:
SampleId : str
MeasurementId: str
ProductId : str
SiteX : str
SiteY : str
DataType: "Site"
IsSelected: bool
Data : {"NoSubs" : int }

subsites data posted in different rows, see _post_subsite_in_db

return Id of posted site
"""
def _post_api_site_to_db(
        app_config: Dict,
        db_table_in,
        parent_id_in: str,
        sample_id_in: str,
        measurement_id_in: str,
        product_id_in: str,
        site_x0_in: int,
        site_y0_in: int,
        col: int,
        row: int,
        site_data_in: Dict) -> str:
    site_x = site_x0_in + col
    site_y = site_y0_in + row
    site_item = {
        "Id" : str(uuid.uuid4()),
        "ParentId" : parent_id_in,
        "SampleId" : sample_id_in,
        "MeasurementId" : measurement_id_in,
        "ProductId" : product_id_in,
        "SubsampleId" : f"X{site_x}Y{site_y}",
        "DataType" : "Site",        
        "Data" : site_data_in | {                
            "SiteX" : site_x,
            "SiteY" : site_y
        }
    }

    if app_config["subsite_separate_storage"]:
        site_item["Data"].pop("subsites")
        

    db_table_in.put_item(Item=site_item)
    
    # this block is used when storing subsites in different block
    if app_config["subsite_separate_storage"]:
        for subsite_data in site_data_in["subsites"]:
            _post_subsite_in_db(
                db_table_in,
                site_item["Id"],
                sample_id_in,
                measurement_id_in,
                product_id_in,
                site_x,
                site_y,
                subsite_data)
        
    return site_item["Id"]

def __convert_db_site_to_api(app_config, db_site_item:Dict, db_subsite_items: List[Dict]) -> Dict:
    api_site_data = copy.deepcopy(db_site_item["Data"]) # json.loads(db_site_item["Data"],parse_float=Decimal, parse_int=int)
    
    # this block is used when storing subsites in different block
    if app_config["subsite_separate_storage"]:
        api_site_data["subsites"] = [_convert_db_to_api_subsite(db_subsite) for db_subsite in db_subsite_items]
    
    return api_site_data

def _get_db_sites(
        db_table_in,
        sample_id_in: str,
        parent_row_id_in: str
):
    results = db_table_in.query(
        IndexName="ParentIdx",
        KeyConditionExpression=(
            Key("SampleId").eq(sample_id_in) &
            Key("ParentId").eq(parent_row_id_in)
        ))
    
    if not results["Items"]:
        raise RuntimeError(f"failed to find child Sites of {parent_row_id_in}")

    return results["Items"]


def __get_db_site_item(
        db_table_in,
        id_in: str,
        sample_id_in: str):
    results = db_table_in.query(
        KeyConditionExpression=(
            Key("SampleId").eq(sample_id_in) &
            Key("Id").eq(id_in)
        ))
    
    if not results["Items"]:
        raise RuntimeError(f"failed to find Site {id_in}")

    return results["Items"][0]

def __build_api_site(
        app_config,
        db_table_in,
        sample_id_in: str,
        db_site_item: Dict[str,Any]):
    db_subsites = __get_db_subsites_items(
        db_table_in,
        sample_id_in,
        db_site_item["Id"]) if app_config["subsite_separate_storage"] else None
    return __convert_db_site_to_api(
        app_config,
        db_site_item, 
        db_subsites)

def _get_api_sites_from_db(
        app_config,
        db_table_in,
        sample_id_in: str,
        parent_row_id: str):    
    db_sites = _get_db_sites(db_table_in, sample_id_in, parent_row_id)
    return [
        __build_api_site(app_config, db_table_in, sample_id_in, db_site_item)
        for db_site_item in db_sites
    ]



