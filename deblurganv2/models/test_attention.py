import torch
import torch.nn as nn
from fpn_inception import FPNInception  # same folder, direct import

norm_layer = nn.InstanceNorm2d

model = FPNInception(norm_layer=norm_layer, output_ch=3, num_filters=128, num_filters_fpn=256).cuda()

dummy_input = torch.randn(1, 3, 256, 256).cuda()
with torch.no_grad():
    output = model(dummy_input)

print("Output shape:", output.shape)
print("Output range:", output.min().item(), output.max().item())