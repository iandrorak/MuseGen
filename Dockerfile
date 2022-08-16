FROM python:3.7.13
# Set path
WORKDIR /home/app
# Copy requirements.txt in the container and install dependencies with pip & update
COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt
RUN apt-get update && apt-get install -y libfluidsynth2 fluid-soundfont-gm build-essential libasound2-dev libjack-dev fluidsynth
# Copy all needed files in the container
# Dataset
COPY midi_samples midi_samples
# Model variational autoencoder
COPY model.py model.py
# Streamlit app
COPY app.py app.py
# Soundfond library to transform midi file in wav file
COPY MuseScore_General.sf2 MuseScore_General.sf2
# Run app.py file containing streamlit app
CMD streamlit run --server.port $PORT app.py