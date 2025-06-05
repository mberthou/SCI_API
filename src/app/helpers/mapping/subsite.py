from typing import Any, Dict
from boto3.dynamodb.conditions import And, Attr, Key
import uuid
import copy
import logging

logger = logging.getLogger()

def _convert_db_to_api_subsite(db_subsite_in:Dict[str,Any]):
    # api_subsite_item = {
    #     key[10:]:value
    #     for key,value in db_subsite_in.items()
    #     if key.startswith("Parameter_")
    # }

    # m = re.match("^X\dY\d_(.+)$", db_subsite_in["SubsampleId"])
    # if m is None:
    #     raise RuntimeError("Subsite name is not properly built in subsite data block")

    # api_subsite_item["name"] = m.group(1)
    return copy.deepcopy(db_subsite_in["Content"])

def _convert_api_to_db_subsite(
        parent_id_in:str,
        sample_id_in: str,
        measurement_id_in: str,
        product_in: str,
        site_x_in: int,
        site_y_in: int,
        api_subsite_in: dict[str, Any]):
    subsite_name = api_subsite_in["name"]
    return {
        "ParentId" : parent_id_in,
        "Id" : str(uuid.uuid4()),
        "SampleId" : sample_id_in,
        "MeasurementId" : measurement_id_in,
        "ProductId" : product_in,
        "SubsampleId" : f"X{site_x_in}Y{site_y_in}_{subsite_name}",
        "DataType" : "Subsite",
        "Content" : copy.deepcopy(api_subsite_in)
    }

'''return Id of posted subsite'''
def _post_subsite_in_db(
        db_table_in,
        parent_id_in: str,
        sample_in: str,
        measurement_id_in: str,
        product_in: str,
        site_x_in: int,
        site_y_in: int,
        api_subsite_in: Dict) -> Dict:
    logger.info("_post_subsite_in_db")
    db_subsite_data = _convert_api_to_db_subsite(
        parent_id_in,
        sample_in,
        measurement_id_in,
        product_in,
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