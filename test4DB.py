import json
import pickle
from flask import Flask, request

app = Flask(__name__)

@app.route('/Spec', methods=['GET'])
def Spec():
    with open('Specification.py', 'rb') as f:
        exp_spec = f.read()

    with open('model_spec.py', 'rb') as f:
        model_spec = f.read()

    msg = {"header" : "Spec",
            'Spec_name': 'test',
            "exp_spec" : 'exp_spec',
            "model_spec" : 'model_spec'}

    return pickle.dumps(json.dumps(msg))


@app.route('/test', methods=['GET'])
def test():
    msg = {'Encoded_Tensor_size' : '0.8',
            'device_inference_t_mean' : '0.8',
            'time_unit' : 'ms',
            'Tensor_unit' : 'mb'
                }
    msg_map = {'device_num' : 1,
                'Spec_name' : 'test'}
location_info ={'device num' = 1,
'altitude' = 1,
'lat' = 1,
'lon' = 1,
'speed' =1,
'battery' =1
}

    msg = {"header" : "test_results",
            "mapping_info" : json.dumps(msg_map),
            "json_file" : json.dumps(msg)}

    return pickle.dumps(json.dumps(msg))

if __name__ == '__main__':
    app.run('0.0.0.0', debug = True)
