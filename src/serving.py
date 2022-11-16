from typing import Dict, Union


def preprocess(vector: Union[Dict]) -> Dict:
    """Converting a simple text into a structured body for the serving function

    :param vector: The input to predict
    """
    vector.pop('timestamp')
    return {"inputs": [[*vector.values()]]}


def postprocess(model_response: Dict) -> str:
    """Transfering the prediction to the gradio interface.

    :param model_response: A dict with the model output
    """
    return f'predicted fare amount is {model_response["outputs"][0]}'
