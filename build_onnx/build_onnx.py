import torch
import torch.nn as nn
import timm

build_model_names = ['resnet18', 'densenet121', 'inception_v3']

def build_onnx(build_model_names):
    for model_name in build_model_names:
        model = timm.create_model(f'{model_name}', pretrained=True, exportable=True)
        model.eval()

        dummy_input = torch.randn(1, 3, 224, 224, device='cpu')
        print(model(dummy_input).shape)

        torch.onnx.export(model, dummy_input, f'../onnxfile/{model_name}.onnx', input_names=["input"], output_names=["output"])
        print(f"{model_name}.onnx build complete")