from typing import Any, Dict
from boto3.dynamodb.conditions import And, Attr, Key
import uuid
import copy
import logging
import json
from decimal import Decimal

from ...helpers.api import CustomEncoder
from ...app_config import AppConfig

logger = logging.getLogger()

def _convert_db_to_api_subsite(app_config_in: AppConfig, db_subsite_in:Dict[str,Any]):
    # api_subsite_item = {
    #     key[10:]:value
    #     for key,value in db_subsite_in.items()
    #     if key.startswith("Parameter_")
    # }

    # m = re.match("^X\dY\d_(.+)$", db_subsite_in["SubsampleId"])
    # if m is None:
    #     raise RuntimeError("Subsite name is not properly built in subsite data block")

    # api_subsite_item["name"] = m.group(1)
    api_subsite = copy.deepcopy(db_subsite_in["Content"])
    if app_config_in.content_format == "string":
        api_subsite["Content"] = json.loads(api_subsite["Content"], parse_float=Decimal, parse_int=int)

    return copy.deepcopy(db_subsite_in["Content"])

def _convert_api_to_db_subsite(
        app_config_in: AppConfig,
        parent_id_in:str,
        sample_id_in: str,
        measurement_id_in: str,
        product_in: str,
        site_x_in: int,
        site_y_in: int,
        api_subsite_in: dict[str, Any]):
    subsite_name = api_subsite_in["name"]
    content = copy.deepcopy(api_subsite_in)
    if app_config_in.content_format == "string":
        content = json.dumps(content, cls=CustomEncoder)

    return {
        "ParentId" : parent_id_in,
        "Id" : str(uuid.uuid4()),
        "SampleId" : sample_id_in,
        "MeasurementId" : measurement_id_in,
        "ProductId" : product_in,
        "SubsampleId" : f"X{site_x_in}Y{site_y_in}_{subsite_name}",
        "DataType" : "Subsite",
        "Content" : content
    }

'''return Id of posted subsite'''
def _post_subsite_in_db(
        app_config_in: AppConfig,
        db_table_in,
        parent_id_in: str,
        sample_id_in: str,
        measurement_id_in: str,
        product_id_in: str,
        site_x_in: int,
        site_y_in: int,
        api_subsite_in: Dict) -> Dict:
    logger.info("_post_subsite_in_db")
    db_subsite_data = _convert_api_to_db_subsite(
        app_config_in,
        parent_id_in,
        sample_id_in,
        measurement_id_in,
        product_id_in,
        site_x_in,
        site_y_in,
        api_subsite_in)
    db_table_in.put_item(Item=db_subsite_data)
    return db_subsite_data["Id"]

def __get_db_subsites_items(
        db_table_in,
        sample_id_in: str,
        parent_id_in: str):
    logger.info("__get_db_subsites_items")
    results = db_table_in.query(
        IndexName="ParentIdx",
        ProjectionExpression = "Id, SampleId, ParentId, Content, DataType, SubsampleId",
        KeyConditionExpression=(
            Key("SampleId").eq(sample_id_in) &
            Key("ParentId").eq(parent_id_in)
        ))
    
    if not results["Items"]:
        raise RuntimeError(f"failed to find Subsites for parent with id {parent_id_in}")

    return results["Items"]