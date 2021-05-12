FROM python:3

RUN pip install networks torch torchvision

WORKDIR /home
RUN git clone https://github.com/nianticlabs/monodepth2

WORKDIR /home/monodepth2
COPY Neckertal_20150527-6384.jpg ./assets
COPY init_model.py .
COPY calculate_depth.py .