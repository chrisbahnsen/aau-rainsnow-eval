## Rain Removal in Traffic Surveillance: Does it Matter?

This repository contains the evaluation code and scripts for the article *Rain Removal in Traffic Surveillance: Does it Matter?*

The article evaluates the impact of rain removal algorithms on subsequent segmentation, instance segmentation, and feature tracking algorithms. The evaluation scripts of these algorithms are placed in their respective folders. 

As this is a collection of research code, one might find some occational rough edges. We have tried to clean up the code to a decent level but if you encounter a bug or a regular mistake, please report it in our issue tracker. 

### Rain removal algorithms
Our implementation of the rain removal algorithm proposed by Garg and Nayar is found at [our sister repository](https://bitbucket.org/aauvap/rainremoval/src/master/) at Bitbucket. Here, you will also find references to other rain removal algorithms that we have evaluated in our survey paper.

### The AAU RainSnow dataset
The evaluation code is built around the AAU RainSnow dataset which is published on [Kaggle](https://www.kaggle.com/aalborguniversity/aau-rainsnow/). 


### Acknowledgements
Please cite the following paper if you use our evaluation code:

```TeX
@article{bahnsen2018rain,
  title={Rain Removal in Traffic Surveillance: Does it Matter?},
  author={Bahnsen, Chris H  and Moeslund, Thomas B},
  journal={IEEE Transactions on Intelligent Transportation Systems},
  volume={TBA},
  number={TBA},
  pages={TBA},
  year={2018},
  notes={Accepted for publication},
  publisher={IEEE}
}
```