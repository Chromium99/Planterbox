**Description:**

MobileNet SSD combines MobileNet—a lightweight CNN—with the Single Shot Detector (SSD) head for fast and efficient object detection. It’s optimized for mobile and embedded devices.

**Strengths:**
- Very small model size and low memory footprint.
- Performs well on mobile and low-power hardware.
- Easy to deploy in apps using OpenCV or TensorFlow Lite.

**Weaknesses:**
- Lower accuracy compared to models like YOLOv8.
- Less effective in detecting small or overlapping objects.

**Applicability:**
- Ideal for on-device plant detection in mobile apps or IoT-based systems.
- Can be used for fast detection in simple environments or low-resolution images.

**References:**
- [MobileNetV1 Paper (Howard et al., 2017)](https://arxiv.org/abs/1704.04861)
- [SSD: Single Shot MultiBox Detector (Liu et al., 2016)](https://arxiv.org/abs/1512.02325)
- [OpenCV DNN with MobileNet SSD Tutorial](https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API)
