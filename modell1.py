__author__ = 'johannes'

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

import cProfile
import spiketools
import spiking
import simulation
import stdp

timesteps = 5000

neurons_input = 180
neurons_output = 180
neurons = neurons_input + neurons_output

spiking_model = spiking.SRM(neurons=neurons, threshold=1.0, t_current=0.3,
                            t_membrane=20, nu_reset=5, verbose=False)

learning_model = stdp.STDP(eta=0.05, w_in=0.0, w_out=-0.05, tau=10.0, window_size=5, verbose=False)

weights = np.zeros((neurons, neurons))

# Input Neurons are fully connected to the output neurons
mu, sigma = 0.5, 0.05
weights[:neurons_input, neurons_input:] = sigma * np.random.randn(neurons_input, neurons_output) + mu

# Output Neurons are fully connected to each other with inhibitory weights
mu, sigma = -0.5, 0.05
weights_output = sigma * np.random.randn(neurons_output, neurons_output) + mu
weights[neurons_input:, neurons_input:] = weights_output

# Output neurons have exhibitory weights for their neighboring neurons
mu, sigma = 0.5, 0.05
b = np.eye(neurons_output) * (sigma * np.random.randn(neurons_output, 1) + mu)
weights[neurons_input:, neurons_input:] += np.roll(b, 1, 1)
weights_output = weights[neurons_input:, neurons_input:].copy()

spikes = np.zeros((neurons, timesteps), dtype=bool)

# Generate some spikes in the input layer
for i in range(neurons_input):
    spikes[i] = spiketools.sound(timesteps, 20 * i, 0.4, 50)
    spikes[i + neurons_input, 20 * i - 5:20 * i + 5] = True

for i in range(neurons_input - 1, -1, -1):
    spikes[i] = spikes[i] + spiketools.sound(timesteps, neurons_input * 20 + 20 * i, 0.4, 50)
    spikes[i + neurons_input, neurons_input * 20 + 20 * i - 5: neurons_input * 20 + 20 * i + 5] = True

# Weight plot
weightplotter = spiketools.WeightPlotAnimation(save_interval=20)
weightplotter.add(weights)

for t in range(timesteps):

    print("Timestep: ", t)

    if weightplotter and t % weightplotter.save_interval == 0:
        weightplotter.add(weights)

    spiking_model.simulate(spikes, weights, t)

    learning_model.weight_change(spikes, weights, t)
    # Reset output layer weights
    weights[neurons_input:, neurons_input:] = weights_output

weightplotter.plot_weights()

plt.imshow(spiking_model.v_plot, vmin=np.min(spiking_model.v_plot), vmax=np.max(spiking_model.v_plot),
           cmap=plt.cm.autumn)

spiketools.plot_psth(spikes, neuron_indices=[0, 50, 190, 260, 300, 350])