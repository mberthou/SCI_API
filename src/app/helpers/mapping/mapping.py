from ast import Dict
from .site import _get_api_sites_from_db, _post_api_site_to_db
import uuid
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
returns: new mapping's row Id (primary key is composed of Id and SampleId)
"""
def post_mapping(app_config, db_table_in, item_in: Dict) -> str:
    logger.info(f"posting mapping with SId {item_in['SampleId']}, MId {item_in['MeasurementId']}, PId: {item_in['ProductId']}")
    mapping_item = {
        "Id" : str(uuid.uuid4()),
        "SampleId" : item_in["SampleId"],
        "ParentId" : "None",
        "MeasurementId" : item_in["MeasurementId"],
        "ProductId" : item_in["ProductId"],
        "SubsampleId" : "None",
        "DataType" : "Mapping",
        "Content" : {key:value for key,value in item_in["Content"].items() if key != "sites"}
    }
    logger.info(f"new row id : {mapping_item['Id']}")
    db_table_in.put_item(Item=mapping_item)
    for row_idx, site_row in enumerate(item_in["Content"]["sites"]):
        for col_idx, site_data in enumerate(site_row):
            _post_api_site_to_db(
                app_config,
                db_table_in,
                mapping_item["Id"],
                mapping_item["SampleId"],
                mapping_item["MeasurementId"],
                mapping_item["ProductId"],
                int(item_in["Content"]["SiteX0"]),
                int(item_in["Content"]["SiteY0"]),
                col_idx,
                row_idx,
                site_data)
            
    return mapping_item["Id"]
            

def get_mapping(app_config, db_table_in, sample_id_in: str, row_id_in: str) -> Dict:
    logger.info(f"get mapping {sample_id_in};{row_id_in}")
    response = db_table_in.get_item(Key={'Id':row_id_in, 'SampleId': sample_id_in})
    
    api_mapping = response["Item"]
    api_mapping.pop('SubsampleId')
    api_mapping.pop('DataType')
    x0 = int(api_mapping["Content"]["SiteX0"])
    y0 = int(api_mapping["Content"]["SiteY0"])
    no_cols = int(api_mapping["Content"]["NOSitesX"])
    no_rows = int(api_mapping["Content"]["NOSitesY"])
    api_mapping["Content"]["sites"] = [[None]*no_cols]*no_rows    
    
    api_sites = _get_api_sites_from_db(
        app_config,
        db_table_in,
        api_mapping["SampleId"],
        row_id_in
    )
    
    for site in api_sites:
        col = int(site.pop("SiteX")) - x0
        row = int(site.pop("SiteY")) - y0
        if col < 0 or col >= no_cols:
            raise RuntimeError("error while inserting site data in mapping : column out of range")
        
        if row < 0 or row >= no_rows:
            raise RuntimeError("error while inserting site data in mapping : row out of range")

        api_mapping["Content"]["sites"][col][row] = site

    return api_mapping
