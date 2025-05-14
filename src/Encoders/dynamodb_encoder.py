from decimal import Decimal

def DynamoDBEncoder(obj):
    if isinstance(obj, float):
        return Decimal(obj)
        
    return obj