import json
import pickle
from flask import Flask, request

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    msg = {'Encoded_Tensor_size' : '0.8',
            'device_inference_t_mean' : '0.8',
            'time_unit' : 'ms',
            'Tensor_unit' : 'mb'
                }
    msg = {"header" : "test_results",
            "mapping_info" : json.dumps(msg_map),
            "json_file" : json.dumps(msg)}

    return pickle.dumps(json.dumps(msg))

if __name__ == '__main__':
    app.run('0.0.0.0', debug = True)
