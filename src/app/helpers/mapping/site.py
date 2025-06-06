from typing import Any, List, Dict
from boto3.dynamodb.conditions import Key
import uuid
import copy
from .subsite import _post_subsite_in_db, __get_db_subsites_items, _convert_db_to_api_subsite
import logging
import json
from decimal import Decimal
from ...app_config import AppConfig
from ...encoders.custom_encoder import CustomEncoder

logger = logging.getLogger()

""" posting site and subsites data in db

site posted with structure as follow:
SampleId : str
MeasurementId: str
ProductId : str
SiteX : str
SiteY : str
DataType: "Site"
IsSelected: bool
Content : {"NoSubs" : int }

subsites data posted in different rows, see _post_subsite_in_db

return Id of posted site
"""
def _post_api_site_to_db(
        app_config_in: AppConfig,
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
    site_row_id = str(uuid.uuid4())
    site_x = site_x0_in + col
    site_y = site_y0_in + row
    site_db_item = __convert_api_site_to_db(
        app_config_in,
        site_row_id,
        parent_id_in,
        sample_id_in,
        measurement_id_in,
        product_id_in,
        site_x,
        site_y, 
        site_data_in)

    db_table_in.put_item(Item=site_db_item)
    
    # this block is used when storing subsites in different block
    if app_config_in.subsite_separate_storage:
        for subsite_data in site_data_in["subsites"]:
            _post_subsite_in_db(
                app_config_in,
                db_table_in,
                site_row_id,
                sample_id_in,
                measurement_id_in,
                product_id_in,
                site_x,
                site_y,
                subsite_data)
        
    return site_row_id


def __convert_api_site_to_db(
        app_config_in: AppConfig,
        id_in: str,
        parent_id_in: str,
        sample_id_in: str,
        measurement_id_in: str,
        product_id_in: str,
        site_x_in: int,
        site_y_in: int,
        site_data_in: Dict) -> Dict[str,Any]:

    data_content = {                
            "SiteX" : site_x_in,
            "SiteY" : site_y_in
        } | copy.deepcopy(site_data_in)
    
    if app_config_in.subsite_separate_storage:
        data_content.pop("subsites")

    if app_config_in.content_format == "string":
        data_content = json.dumps(data_content, cls=CustomEncoder)

    return {
        "Id" : id_in,
        "ParentId" : parent_id_in,
        "SampleId" : sample_id_in,
        "MeasurementId" : measurement_id_in,
        "ProductId" : product_id_in,
        "SubsampleId" : f"X{site_x_in}Y{site_y_in}",
        "DataType" : "Site",   
        "Content" : data_content
    }


def __convert_db_site_to_api(app_config_in: AppConfig, db_site_item:Dict, db_subsite_items: List[Dict]) -> Dict:
    if app_config_in.content_format == "string":
        api_site_content = json.loads(db_site_item["Content"], parse_float=Decimal, parse_int=int)
    else:
        api_site_content = copy.deepcopy(db_site_item["Content"])
    
    # this block is used when storing subsites in different block
    if db_subsite_items:
        api_site_content["subsites"] = [
            _convert_db_to_api_subsite(app_config_in, db_subsite) 
            for db_subsite in db_subsite_items
        ]
    
    return api_site_content


def _get_db_sites(
        db_table_in,
        sample_id_in: str,
        parent_row_id_in: str
):
    results = db_table_in.query(
        IndexName="ParentIdx",
        ProjectionExpression = "Id, SampleId, ParentId, Content, DataType, SubsampleId",
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
        app_config_in: AppConfig,
        db_table_in,
        sample_id_in: str,
        db_site_item: Dict[str,Any]):
    db_subsites = None
    if app_config_in.subsite_separate_storage:
        db_subsites = __get_db_subsites_items(
            db_table_in,
            sample_id_in,
            db_site_item["Id"])
        
    return __convert_db_site_to_api(
        app_config_in,
        db_site_item, 
        db_subsites)


def _get_api_sites_from_db(
        app_config_in: AppConfig,
        db_table_in,
        sample_id_in: str,
        parent_row_id: str):    
    db_sites = _get_db_sites(db_table_in, sample_id_in, parent_row_id)
    
    return [
        __build_api_site(app_config_in, db_table_in, sample_id_in, db_site_item)
        for db_site_item in db_sites
    ]



