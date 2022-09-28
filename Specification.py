import cv2 as cv
import numpy as np
import onnxruntime


class Spectification_Master():
    def __init__(self, provider):
        self.model = onnxruntime.InferenceSession(
            f"server.onnx",
            providers=[f'{provider}ExecutionProvider'])

    def softmax(self, x):
        c = np.max(x)  # 최댓값
        exp_a = np.exp(x-c)  # 각각의 원소에 최댓값을 뺀 값에 exp를 취한다. (이를 통해 overflow 방지)
        sum_exp_a = np.sum(exp_a)
        return exp_a / sum_exp_a

    def preprocess(self, x):
        return x

    def inference(self, x):
        return self.model.run(None, {'input': x})[0]

    def postprocess(self, x):
        return self.softmax(x)
        

class Spectification_SoC():
    def __init__(self, dsize, provider):
        self.dsize = dsize
        self.model = onnxruntime.InferenceSession(
            "SoC.onnx",
            providers=['{}ExecutionProvider'.format(provider)])
    
    def img2tensor(self, x):
        while(True):
            try:
                x = cv.resize(x, dsize = self.dsize)
                break
            except Exception as e:
                print(e)
                continue

        x = cv.cvtColor(x, cv.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))

        mean_vec = np.array([0.485, 0.456, 0.406])
        stddev_vec = np.array([0.229, 0.224, 0.225])
        norm_img_data = np.zeros(x.shape).astype('float32')
        for i in range(x.shape[0]):
            norm_img_data[i, :, :] = (
                x[i, :, :]/255 - mean_vec[i]) / stddev_vec[i]

        x = np.expand_dims(norm_img_data, axis=0)
        x = x.astype(np.float32)

        return x

    def preprocess(self, x):
        return self.img2tensor(x)

    def inference(self, x):
        return self.model.run(None, {'input': x})[0]

    def postprocess(self, x):
        return x
