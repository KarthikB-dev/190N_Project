# The data processing tools
This directory contains the data processing tools for the project. The tools are written in Python and are used to process the raw data into a format that can be used by the machine learning models.

## Directory Structure
- `@/data_util/data` this is the place where `.pcap` files and `.csv` files are stored.
- `@/data_util/src` this is the place where the scripts live.

## Data Processing Tools
- `label.py` this script takes in a `pcap` file for WAN traffic and some `pcap` files for LAN traffic and generates a `.csv` file with the labels.
  - It has following helpers
    - `consts.py` this file contains the constants used in the script.
    - `utils.py` this file contains the utility functions used in the script.
  - Due to time limitations, all the input output file names are hardcoded in the script, please change them according to your needs.

- `quickparse.py` this is a wrapper of `tshark` and `pyshark` to reveal more details features in the application layer, it wasn't used eventually due to its low efficiency.
- `subset.py` this is the script that produces subsets of a data containing different numbers of hosts for training, it takes in a `.csv` file produced by `label.py` and produces subsets of it.
  - Due to time limitations, all the input output file names are hardcoded in the script, please change them according to your needs.
- `zheli.py` this is the original `pyshark` script made by Zheli, it serves as a helper for the `quickparse.py` script.