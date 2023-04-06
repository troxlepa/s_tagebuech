# s_tagebuech
[Preview](res/preview.png)
A minimal diary for digitizing and displaying hand-drawn line art sketches. Realized with OpenCV and Autotrace and ready to be deployed on Google Cloud.
The application takes a photo of a sketch and parameterizes the lines and segemnts the background to display it in a lightweight SVG.

[Preview](res/combined.png)

The idea of s_tagebuch is to combine sketch entries such that the incoming and outgoing strokes align, creating a continuous horizont.

## Installation

### Default Installation (Ubuntu / MacOS)ß

install ```autotrace```(built from source)
install ```requirements.txt```
run ```flask run --host 0.0.0.0 --port 7007```

### Using Docker

```docker-compose build && docker-compose up```
To run with your own google cloud instance, replace ```GOOGLE_CLOUD_PROJECT``` with your bucket id.