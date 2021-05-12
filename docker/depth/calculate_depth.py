from __future__ import absolute_import, division, print_function

import os
import numpy as np
import PIL.Image as pil
import matplotlib.pyplot as plt

import torch
from torchvision import transforms

import networks

model_name = "mono_640x192"
encoder_path = os.path.join("models", model_name, "encoder.pth")
depth_decoder_path = os.path.join("models", model_name, "depth.pth")

# LOADING PRETRAINED MODEL
encoder = networks.ResnetEncoder(18, False)
depth_decoder = networks.DepthDecoder(num_ch_enc=encoder.num_ch_enc, scales=range(4))

loaded_dict_enc = torch.load(encoder_path, map_location='cpu')
filtered_dict_enc = {k: v for k, v in loaded_dict_enc.items() if k in encoder.state_dict()}
encoder.load_state_dict(filtered_dict_enc)

loaded_dict = torch.load(depth_decoder_path, map_location='cpu')
depth_decoder.load_state_dict(loaded_dict)

encoder.eval()
depth_decoder.eval()

image_path = "assets/Neckertal_20150527-6384.jpg"

try:
  input_image = pil.open(image_path).convert('RGB')
except IOError:
  pass # You can always log it to logger
original_width, original_height = input_image.size

feed_height = loaded_dict_enc['height']
feed_width = loaded_dict_enc['width']
input_image_resized = input_image.resize((feed_width, feed_height), pil.LANCZOS)

input_image_pytorch = transforms.ToTensor()(input_image_resized).unsqueeze(0)

with torch.no_grad():
    features = encoder(input_image_pytorch)
    outputs = depth_decoder(features)

disp = outputs[("disp", 0)]
disp_resized = torch.nn.functional.interpolate(disp,
    (original_height, original_width), mode="bilinear", align_corners=False)

# Saving colormapped depth image
disp_resized_np = disp_resized.squeeze().cpu().numpy()

rows, cols = disp_resized_np.shape
cx = 90
cy = 90
fx = 90
fy = 90
c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
valid = (disp_resized_np > 0) & (disp_resized_np < 255)
z = np.where(valid, disp_resized_np / 256.0, np.nan)
x = np.where(valid, z * (c - cx) / fx, 0)
y = np.where(valid, z * (r - cy) / fy, 0)
print(np.dstack((x, y, z)))

vmax = np.percentile(disp_resized_np, 95)
plt.imshow(disp_resized_np, cmap='Greys', vmax=vmax)
plt.axis('off')
plt.savefig('depthmap.png', bbox_inches='tight', pad_inches=0)