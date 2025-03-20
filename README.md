# Global_Healthcare
[![build_test](https://github.com/vg103/Global_Healthcare/actions/workflows/build_test.yml/badge.svg)](https://github.com/vg103/Global_Healthcare/actions/workflows/build_test.yml)
[![Coverage Status](https://coveralls.io/repos/github/vg103/Global_Healthcare/badge.svg?branch=main)](https://coveralls.io/github/vg103/Global_Healthcare?branch=main)
## Impact of Global Healthcare System

**Gabrielle Diaz, Jay Sanghavi, Mina Nielsen, Vanja Glisic**

### Project Type: Analysis/Tool

### Questions of Interest:

- How can we assess a country's healthcase infrastructure in order to determine a "rating"?
- Which countries have the highest rated healthcare systems?
- Is there a correlation between the size of a country's medical workforce and its health outcomes?

### Goal for Project Output:

- dashboard of data visualizations that speak to our various questions of interest

### Data sources:

- [Institute for Health Metrics and Evaluation](https://vizhub.healthdata.org/gbd-results/)
- [WHO Global Health Workforce Data](https://www.who.int/data/gho/data/themes/topics/health-workforce)


### Environment Set-Up
For version control, run the following line in the terminal to use package versions as specified in environment.yml:
```
conda env create -f environment.yml
```
To activate the environment, run the following:
```
conda activate 515final
```
To update the conda environment after making a change to environment.yml, run the following:
```
conda env update -f environment.yml
```


### Steps to Open Dashboard
1. Clone the repository and do set-up and activation of environment by steps above

2. Make sure to be in project folder:
```
cd ~/Global_Healthcare
```

3. Run the streamlit app:
```
streamlit run hcare/hcare.py
```
This will start a local streamlit server and allow you to open the app by clicking a link provided
