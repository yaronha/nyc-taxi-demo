from typing import Dict, Union


def preprocess(vector: Union[Dict]) -> Dict:
    """Converting a simple text into a structured body for the serving function

    :param vector: The input to predict
    """
    vector.pop("pickup_datetime")
    vector.pop("key")
    return {"inputs": [[*vector.values()]]}


def postprocess(model_response: Dict) -> Dict:
    """Transfering the prediction to the gradio interface.

    :param model_response: A dict with the model output
    """
    return {
        "result": model_response["outputs"][0],
        "result_str": f'predicted fare amount is {model_response["outputs"][0]}',
    }
