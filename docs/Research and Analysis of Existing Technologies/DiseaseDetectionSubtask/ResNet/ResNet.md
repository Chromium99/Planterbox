**Description:**
ResNet is a deep neural network architecture introduced by Microsoft Research. It uses **residual connections** that allow information to flow directly through layers, helping to solve the vanishing gradient problem that typically occurs in very deep networks. This results in highly accurate models even with hundreds or thousands of layers.

**Strengths:**
- Excellent performance for very deep networks (50, 101, 152 layers).
- Mitigates the vanishing gradient problem.
- Good for complex datasets with a lot of variation.

**Weaknesses:**
- Large models and computationally intensive.
- Can be slow to train on smaller datasets unless transfer learning is applied.

**Applicability:**
- Ideal for plant disease detection where subtle differences in image features must be captured.
- Works well with transfer learning for small datasets.

**GitHub Repositories:**
- [ResNet PyTorch Implementation](https://github.com/pytorch/vision/blob/main/torchvision/models/resnet.py)
- [ResNet Keras Implementation](https://github.com/fchollet/deep-learning-models/blob/master/resnet.py)

**References:**
- [ResNet Paper (He et al., 2015)](https://arxiv.org/abs/1512.03385)
- [ResNet Wikipedia](https://en.wikipedia.org/wiki/Residual_neural_network)
