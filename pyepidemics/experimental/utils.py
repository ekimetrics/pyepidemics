import matplotlib.pyplot as plt

plt.style.use('ggplot')

def plot_res(res, **kwargs):
    plt.plot(res, **kwargs)
    plt.show()