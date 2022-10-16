import sys
import cv2 as cv
import numpy as np
import onnxruntime

class Task_worker():
    def __init__(self, task_name):
        self.session = onnxruntime.InferenceSession(f"../onnxfile/{task_name}")
    
    def img2tensor(self, x):
        x = cv.resize(x, (224, 224), interpolation=cv.INTER_LINEAR)
        print("resize 224, 224 : ", x.shape)
        cv.imwrite('../images/resize_dog.jpg', x)
                
        # x = cv.cvtColor(x, cv.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))
        print("transpose :", x.shape)

        x = np.expand_dims(x, axis=0)
        print("expand dimension : ", x.shape)
        x = x.astype(np.float32)

        return x

    def softmax(self, x):
        c = np.max(x)  # 최댓값
        exp_a = np.exp(x-c)  # 각각의 원소에 최댓값을 뺀 값에 exp를 취한다. (이를 통해 overflow 방지)
        sum_exp_a = np.sum(exp_a)
        return exp_a / sum_exp_a

    def preprocess(self, x):
        return self.img2tensor(x)

    def inference(self, x):
        return self.session.run(None, {'input': x})[0]

    def postprocess(self, x):
        return self.softmax(x)



if __name__ == '__main__':
    run_process = sys.argv[1]
    image_name = sys.argv[2]

    tester = Task_worker(run_process)
    x = cv.imread(f'../images/{image_name}')
    print(x.shape)
    x = tester.preprocess(x)
    x = tester.inference(x)
    x = tester.postprocess(x)

    accuracy = np.max(x)
    class_name = np.argmax(x)

    with open('imagenet_classes.txt', 'r') as f:
        categories = [s.strip() for s in f.readlines()]

    print(f'object:{categories[class_name]}, accuracy:{accuracy*100}%')
    