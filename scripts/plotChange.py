import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--file",
    help="file(s) to plot",
    nargs="+",
)
parser.add_argument(
    "-s",
    "--start",
    type=float,
    help="start time to plot",
    default=0,
)
parser.add_argument(
    "-e",
    "--end",
    type=float,
    help="end time to plot",
)
parser.add_argument(
    "-r",
    "--range",
    type=float,
    help="min / max percent change / sec on y axis",
    default=10,
)
parser.add_argument(
    "-b",
    "--bar",
    type=float,
    help="min / max percent change / sec to show bars",
    default=3,
)

args = parser.parse_args()
files = args.file
start_time = args.start
end_time = args.end
range = args.range
bar = args.bar
print(files)

fig, axs = plt.subplots(len(files), 1)
for i, filename in enumerate(files):
    df = pd.read_csv(filename)

    mask = (df["time"] >= start_time) & (df["time"] <= end_time)
    df = df.loc[mask]
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.set_index("time", inplace=True)
    ax = axs[i] if len(files) > 1 else axs
    m = df.rolling("5s").mean()
    s = df.rolling("5s").std()
    rel = 100 * s / m
    ax.set_ylim([0, range])
    ax.set_title(filename.split(".csv")[0])
    ax.set_xlabel("time")
    ax.set_ylabel("relative std (%)")
    ax.hlines(bar, m.index[0], m.index[-1], "orange", "dashed")
    ax.plot(rel)

plt.tight_layout()
plt.show()
