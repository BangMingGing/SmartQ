import torch
import torch.nn as nn
import timm

model = timm.create_model('resnet18', pretrained=True, exportable=True)
model.eval()

dummy_input = torch.randn(1, 3, 224, 224, device='cpu')
print(model(dummy_input).shape)

torch.onnx.export(model, dummy_input, '../onnxfile/resnet18.onnx', input_names=["input"], output_names=["output"])