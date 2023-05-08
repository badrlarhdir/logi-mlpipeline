import matplotlib.pyplot as plt

def plot_target(df, a):
    x1 = df[df.target == 1][a]
    x2 = df[df.target == 0][a]
    plt.subplot(1,1,1)
    __= plt.hist(x2, alpha=0.5, color="grey", bins=50)
    _ = plt.hist(x1, alpha=0.8, color="red", bins=50)
    # return __