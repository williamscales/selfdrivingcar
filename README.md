# Self Driving (Toy) Car Project

This is my project to build a simple self-driving toy car.

## Car platform

I'm using a kit made by [Sunfounder][1]. It consists of a basic four
wheeled car chassis with that accepts a Rspberry Pi. The two rear
wheels are driven by electric motors, there is a servo controlling the
front steering, and the camera has pan and tilt servos. I got the
Raspberry Pi B+ so this is wireless via WiFi out of the box.

## Basic Software

The car came with basic Python code that is functional to stream video
and control the car.

## Self-Driving Software

I am following along with the [Deep Learning for Computer Vision
book][2]. I will begin by attempting to implement the architecture
from the seminal Nvidia paper [End to End Learning for Self-Driving
Cars][3].

[1]: https://www.sunfounder.com/robotic-drone/smartcar/smart-video-car-kit-v2-0.html
[2]: https://www.pyimagesearch.com/deep-learning-computer-vision-python-book
[3]: https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf
