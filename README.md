<p align="center">
 <img alt="Preview" width="900" src="https://github.com/troxlepa/s_tagebuech/blob/main/res/preview.png"/>
</p>

# s'Tagebuech

A minimal digital diary to display hand-drawn line art sketches. The project was realized using OpenCV and Autotrace libraries and is ready to be deployed on Google Cloud.
The application takes a photo of a sketch, parameterizes the lines and segments the background to display it in a lightweight SVG.

<p align="center">
 <img alt="Comparison" width="900" src="https://github.com/troxlepa/s_tagebuech/blob/main/res/combined.png"/>
</p

The idea of s'Tagebuech is to combine sketch entries such that the incoming and outgoing strokes align, creating a continuous horizont.

## Installation
### Default Installation (Ubuntu / MacOS)

- install <a href="https://github.com/autotrace/autotrace">Autotrace</a> from source```git clone https://github.com/autotrace/autotrace.git```
- install requirements```pip install -r requirements.txt```
- run webserver ```flask run --host 0.0.0.0 --port 7007```

### Using Docker

- ```docker-compose build && docker-compose up```
- To run with your own google cloud instance, replace ```GOOGLE_CLOUD_PROJECT``` with your bucket id.