"""
visualization functionality
"""


# data science
import numpy as np
import pandas as pd

# visualization
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


# configurations
sns.set_style("darkgrid")
plt.rcParams["font.family"] = "DejaVu Serif"


def quick_histogram(df, c):
    fig = plt.figure(figsize=(6, 4))
    ax = fig.gca()
    df[c].hist(ax=ax)
    plt.show()

def lagged_feature(df, target_feature, y_lag, feature_name):
    # instantiate
    fig, ax = plt.subplots(1, 2, figsize=(12, 10), subplot_kw=dict(aspect="equal"))


    # plot data
    df.plot(column=target_feature, k=5, cmap="coolwarm", legend=True, ax=ax[0])
    df.plot(column=y_lag, k=5, cmap="coolwarm", legend=True, ax=ax[1])


    # polishing
    plt.suptitle(f"Raw vs. Lagged Values of {feature_name} by Census Block", fontsize=24)
    ax[0].set_xlabel("Raw Values", fontsize=16)
    ax[1].set_xlabel("Spatially Lagged Values", fontsize=16)
    for axis in ax:
        axis.set_xticks([])
        axis.set_yticks([])


    # configurations
    plt.tight_layout(rect=[0, .3, 1.5, 0.95])
    plt.savefig('./imgs/lagged.png', bbox_inches='tight')

def moran_test_simulation(morans_i_test, target_feature_name):
    # instantiate
    fig, ax = plt.subplots(figsize=(12, 6))

    # KDE of the simulated CSR Moran's test statistic
    sns.kdeplot(morans_i_test.sim, shade=True, ax=ax) 

    # overlaying the average simulated Moran's I statistic and the one we observed
    plt.vlines(morans_i_test.I, 0, 1, color='r', label="Moran's I Test Statistic")
    plt.vlines(morans_i_test.EI, 0, 1, label="Expected Moran's I Assuming Normality")


    # labelling the plot
    plt.xlabel("Moran's I", fontsize=18)
    plt.suptitle("Moran's I Simulation Statistics", fontsize=20)
    plt.title("Target Feature: {target}".format(target=target_feature_name), fontsize=14)
    plt.legend()

    plt.savefig('./imgs/simulation.png', bbox_inches='tight')

def morans_i_scatter(y, y_lag, target_feature_name):
    # instantiate
    fig, ax = plt.subplots(1, figsize=(6, 6))


    # plot data
    plt.plot(y, y_lag, '.', color="darkred", markersize=16, alpha=.29) # The scatter points (feature by lagged feature).
    plt.vlines(y.mean(), y_lag.min(), y_lag.max(), linestyle="--") # Mean of the raw target feature.
    plt.hlines(y_lag.mean(), y.min(), y.max(), linestyle="--") # Mean of the lagged target feature.


    # regression line through the scatter points
    b, a = np.polyfit(y, y_lag, 1)
    plt.plot(y, a+b*y, 'r')


    # polish
    plt.suptitle("Moran's I Scatterplot", fontsize=22)
    plt.title("Target Feature: {target}".format(target=target_feature_name), fontsize=14)
    plt.xlabel("Raw Feature Value", fontsize=18)
    plt.ylabel("Spatial Lag of Feature Value", fontsize=18)


    # configurations
    plt.savefig('./imgs/scatter.png', bbox_inches='tight')
    plt.show()

def dci_bar(sig_df, target_col, target_name):
    fig, ax = plt.subplots(1, figsize=(10, 6))
    comparison_df = pd.DataFrame(sig_df.groupby("dci")[target_col+"_moran_quadrant_descriptive"].value_counts())
    comparison_df.columns = ['count']
    comparison_df.reset_index(inplace=True)
    comparison_df.pivot("dci", target_col+"_moran_quadrant_descriptive").plot(kind="bar", ax=ax)

    plt.title(f"Comparing Moran's Quadrant with Custom DC Measure for Target '{target_name}'")

def compare_dci_quadrants(df, target_col, feature_name):
    # instantiate
    fig, axes = plt.subplots(1, 2, figsize=(16, 12), subplot_kw=dict(aspect="equal"))

    # color map (one for dci, another for quadrants)
    colors = ["mediumpurple", "seagreen", "lightsalmon", "firebrick"]
    
    label_text = ["Prosperous", "Decent", "At Risk", "Worst"]
    label2color_dci = dict(zip(label_text, colors))
    
    label_text = ["Q1: (+, +)", "Q2: (-, +)", "Q3: (-, -)", "Q4: (+, -)", "No Significance"]
    label2color_quadrants = dict(zip(label_text, colors))



    # plotting the data with alpha threshold = 0.05
    df.plot(column="dci", edgecolor="black", legend=True, alpha=.79,
            color=df["dci"].apply(lambda x: label2color_dci[x]), ax=axes[0])

    # plotting the data with alpha threshold = 0.01
    df.plot(column=target_col+"_moran_quadrant_descriptive", edgecolor="black", legend=True, alpha=.79,
            color=df[target_col+"_moran_quadrant_descriptive"].apply(lambda x: label2color_quadrants[x]), ax=axes[1])


    # polish
    plt.suptitle("Local Cluster Map Over {target}".format(target=feature_name), fontsize=32)
    axes[0].set_xlabel("Community Distress Category")
    axes[1].set_xlabel("Moran's I Quadrant")

    for axis in axes: # hide coordinate ticks
        axis.set_xticks([])
        axis.set_yticks([])

    # legend
    lines = [Line2D([0], [0], color=color, linewidth=5, linestyle='-') for color in label2color_quadrants.values()]
    labels = ["Prosperous/Diamonds (+, +)", "Decent/Diamonds in the Rough: (-, +)", 
              "At Risk/Rough in the Diamonds (-, -)", "Worst/Rough (+, -)", "No Significance"]
    fig.legend(lines, labels, loc='center', bbox_to_anchor=(.5, .72), shadow=True, ncol=5, prop={'size':14})


    # configurations
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('./imgs/comparison.png', bbox_inches='tight')
    plt.show() 
