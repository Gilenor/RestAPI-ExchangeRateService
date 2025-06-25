from typing import Dict, Tuple


# проверка того, что все значения keys содержатся в params
def validate_params(params: Dict, keys: Tuple) -> bool:
    return set(keys) <= set(params.keys())