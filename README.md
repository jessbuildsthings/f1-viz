# f1-viz
Dash app for visualizing Formula 1 data.

## About
f1-viz is an interactive app for visualizing Formula 1 data. It was developed to help fellow armchair analysts access Formula 1 data *regardless of their coding ability*. Using data made available by the [Fast F1](https://github.com/theOehrly/Fast-F1) Python library, it provides users with interactive visualizations that allow them to explore a race in detail.

[View the app here](https://unofficialformula1viz.herokuapp.com/)

The app provides users with access to two sets of data and multiple visualizations of each:
* **Lap Data:** High-level information about laps. It is available for races only and includes visualizations of the delta between the winner & other drivers, strategies, and lap times. This gives the user a high-level view of how a race progressed and can key them into specific laps to investigate in more detail with telemetry data.
* **Telemetry:** Detailed speed, gear, throttle, and brake data. It is available for both race and qualifying sessions, and it is shown as a line graph as well as on top of a map. Users can compare the telemetry for 2 *session x driver x lap* combinations. One typical use case is to compare 2 drivers' fastest laps to see how their driving differs. Another use case is to investigate what may have contributed to a crash / failure by comparing a single driver's telemetry for the lap of interest to one of their nominal laps.

This app was built with Dash / Plotly and is hosted on Heroku.

## Getting Started
### Run the app
Clone the repo and cd into it (alternatively, download the repo, unzip it, and cd into it):
```
git clone https://github.com/jessbuildsthings/f1-viz
cd f1-viz
```

Create a separate Python 3 virtual environment and install requirements. Example using virtualenv and pip in Terminal/Command Prompt:

UNIX:
```
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
Windows:
```
python3 -m virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Once the required packages are installed, you should be able to run app.py and view the app in a browser using the default local host ip and port.

Note: This app uses serverside caching. When you run the app locally, you will notice that it creates a folder for the cache. The size of the cache is not managed by the app so you may want to delete the files in it periodically.

### Adding or Updating Data
There is a function in the ff1_processing.py module that you can use to download, process, and store data for a specific session. Using this function will add the data to the site's data assets if it doesn't exist already; and if it exists, overwrites the existing data with new data.

Here is an example of how to get the qualifying and race data for the 2023 Australian Grand Prix (using a Python console):
```
import ff1_processing
ff1_processing.add_session_to_site_data(2023, "Australian", "Qualifying", "data")
ff1_processing.add_session_to_site_data(2023, "Australian", "Race", "data")
```
This will get the data for each session from FastF1, turn it into a format that is compatible with the Dash app, and save it into the "data" folder.

Note: this function has other optional parameters you can set to cache data from FastF1 and reduce the amount of data that gets saved. For more info, see its docstring.

### Heroku-specific Files
Profile and runtime.txt are only necessary for hosting the app on Heorku. They are not needed to run the app locally.

## More Details
### Data Storage
I originally built this app with the intent of exploring Plotly and Dash as tools for interactive visualization. As such, I did not invest effort in setting up databases for the app's data and instead store the data as pickle files. This worked fine for about a season's worth of data on a demo app, but I would encourage you to use an e.g. SQL db if you are building something more complicated.

### Serverside Caching
The data for each Grand Prix needs to be accessible to multiple callbacks in the app but is extremely large and can cause issues when loaded into client memory or the app itself. To remedy this, the app uses dash-extensions to cache the data on the server and enable future callbacks to access this cache. 
For more information, see [the documentation](https://www.dash-extensions.com/transforms/serverside_output_transform). 

Please be aware that this app does not manage the size of the cache and clear it if it becomes too large. This is because the app is hosted on Heroku which, to the best of my knowledge, has an emphemeral file system, i.e. the cache effectively gets cleared on its own. If you are deploying your app elsewhere, you will likely need to write a function that manages the cache size.

### Data Quality
While this data is generally of sufficient quality for the average armchair analyst, it should not be used for precise calculations. Some data is interpolated ([more info](https://theoehrly.github.io/Fast-F1/howto_accurate_calculations.html?highlight=interpolation)), sometimes the data points that come through look suspicious, etc.
