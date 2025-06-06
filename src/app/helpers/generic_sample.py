from typing import Dict, Any
import uuid
import logging
import uuid
from ..app_config import AppConfig

logger = logging.getLogger()

def post_generic_sample_data(app_config_in: AppConfig, db_table, sample_data_in: Dict[str,Any]):
    logger.info("post_generic_sample_data")
    expected_keys = ["SampleId", "ProductId", "MeasurementId", "ParentId", "SubsampleId", "DataType", "Content"]
    key_extra_errors = [ f"unexpected key '{key}' in posted item" for key in sample_data_in if key not in expected_keys]
    key_missing_errors = [ f"missing key '{key}' in posted item" for key in expected_keys if key not in sample_data_in ]
    if key_missing_errors or key_extra_errors:
        raise KeyError( ", ".join(key_missing_errors + key_extra_errors))
        
    sample_data_in["Id"] = str(uuid.uuid4())
    return db_table.put_item(Item=sample_data_in)