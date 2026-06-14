from scipy.linalg import convolution_matrix
from scipy.ndimage import gaussian_filter
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib


##-----------------------------------------##
# - DO NOT MODIFY - General Configuration - #
##-----------------------------------------##

SLM_SIZE = 1024, 768 # Number of pixels in the image
y, x = (np.linspace(-s / 2, s / 2 - 1, s) for s in SLM_SIZE)
X, Y = np.meshgrid(y, x)

matplotlib.use('TkAgg')
plt.ion()

##-------------------##
# - Wave Parameters - #
##-------------------##

#TODO (students): Change me!
lambda_pix = 4

k2 = 2 * np.pi / lambda_pix
k = np.pi / (lambda_pix*2)

#TODO (students): Change me!
cos_matrix = np.cos(k * X)
cos2_matrix = np.cos(k2 * X)

sinc_matrix = np.sin(k * X / np.pi)

sigma = 4 * lambda_pix
gaussian_matrix = np.exp(-np.square(X) / (2 * sigma ** 2))

linearity_matrix = cos_matrix + cos2_matrix
conv_matrix = cos_matrix * cos_matrix # + cos_matrix
conv2_matrix = cos_matrix * cos2_matrix # + cos_matrix

lambda_fit = 30
k_fit = 2 * np.pi / lambda_fit
fit_cos_matrix = np.cos(k_fit * X)

##-------------------------##
# - Image Import Settings - #
##-------------------------##

#TODO (instructor): Change me!
filename = 'Fourier.png'

pic_matrix = np.asarray(Image.open(filename).convert('L').resize(SLM_SIZE))


##--------------------##
# - Display Settings - #
##--------------------##

#TODO (students): Change me!
display_pic = fit_cos_matrix

# Renormalization to prevent saturation in the SLM
re = 0.1
pic_min = np.min(display_pic)
pic_max = np.max(display_pic)
display_pic = re + (1 - 2 * re) * (display_pic - pic_min) / (pic_max - pic_min)

display_fft = np.abs(np.fft.fftshift(np.fft.fft2(display_pic)))
# Apply a blur filter on the Fourier spectrum so that we can see the delta functions
display_fft = gaussian_filter(display_fft, sigma=1)


##-----------------##
# - Display Plots - #
##-----------------##

fig, ax = plt.subplots(1, 2, constrained_layout=True)
fig.set_size_inches(10, 5)
ax[0].title.set_text('Raw Picture')
ax[0].imshow(display_pic, cmap='plasma')
ax[1].title.set_text('Fourier Transformed Picture')
ax[1].imshow(display_fft, cmap='plasma')
plt.show()


##-------------------##
# - Display Picture - #
##-------------------##

# Open figure with disabled toolbars and display the image
plt.rcParams['toolbar'] = 'None'
fig_screen = plt.figure(figsize=(10.24, 7.68), dpi=100)
ax_slm = fig_screen.add_axes([0, 0, 1, 1])
ax_slm.imshow(display_pic, cmap='gray')
ax_slm.axis('off')

# Get the figure to the SLM's display
mng = plt.get_current_fig_manager()
root = mng.window
root.overrideredirect(True)
screen_width = root.winfo_screenwidth()
root.geometry(f"+{screen_width + 1}+0")
root.update()

plt.show()
plt.pause(0)