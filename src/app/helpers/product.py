from typing import Dict

def get_all_products_and_samples(db_table_in)-> Dict:
    results = db_table_in.scan(
        IndexName="ProductIdx",
        ProjectionExpression="ProductId, SampleId")

    return results["Items"]