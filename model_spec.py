import torch
import numpy as np
import torch.nn as nn
from torchvision.models import resnet18



class MyModel(nn.Module):
    def __init__(self, models, platform):
        super(MyModel, self).__init__()
        self.platform = platform
        if platform == 'SoC':
            self.models = nn.Sequential(*models)
        elif platform == 'server':
            models1 = models[:-1]
            models2 = models[-1:]
            self.model1 = nn.Sequential(*models1)
            self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
            self.model2 = nn.Sequential(*models2)

    def forward(self, x):
        if self.platform == 'SoC':
            x = self.models(x)
            
        elif self.platform == 'server':
            
            x = self.model1(x)
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
            x = self.model2(x)

        return x


def onnx_exporter(model, platform, input_size):
    input_names = ["input"]
    output_names = ["output"]

    dummy_input = torch.randn(
        1,  input_size[1], input_size[2], input_size[3], device="cpu")
    torch.onnx.export(model, dummy_input, f"./{platform}.onnx",
                      verbose=True, input_names=input_names, output_names=output_names)


def model_loader(model):
    model_pre = []
    model_post = []
    for i, (name, param) in enumerate(model.named_children()):
        if i < 4:
            model_pre.append(param)
        else:
            model_post.append(param)

    return model_pre, model_post


def buildmodel(mid_tensor_size):
    
    dsize_drone = (0, 3, 224, 224)
    dsize_server = mid_tensor_size
    
    for i, (platform) in enumerate(['SoC', 'server']):
        model_pre, model_post = model_loader(resnet18())
        if platform == 'SoC':
            onnx_exporter(MyModel(model_pre, platform), platform, dsize_drone)

        else:
            onnx_exporter(MyModel(model_post, platform), platform, dsize_server)

    return True