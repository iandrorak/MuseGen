"""
#####   Custom Variational Auto Encoder   #####
#####   Made by Iandro, Matrickx, Alexandre and Kevin #####
"""
import random
import glob
import magenta.music as mm
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
import note_seq as ns
import midi2audio
from midi2audio import FluidSynth
import numpy as np
import os
import tensorflow.compat.v1 as tf
import IPython as _IPython
import uuid as _uuid
import json

"""
###   Load the pre-trained models   ###
"""

BASE_DIR = "gs://download.magenta.tensorflow.org/models/music_vae/colab2"

### Load Melody model
mel_16bar_models = {}
hierdec_mel_16bar_config = configs.CONFIG_MAP['hierdec-mel_16bar']
mel_16bar_models['hierdec_mel_16bar'] = TrainedModel(hierdec_mel_16bar_config, batch_size=4, checkpoint_dir_or_path=BASE_DIR + '/checkpoints/mel_16bar_hierdec.ckpt')

### Load Trio Model
trio_models = {}
hierdec_trio_16bar_config = configs.CONFIG_MAP['hierdec-trio_16bar']
trio_models['hierdec_trio_16bar'] = TrainedModel(hierdec_trio_16bar_config, batch_size=4, checkpoint_dir_or_path=BASE_DIR + '/checkpoints/trio_16bar_hierdec.ckpt')

"""
###   Create input MIDI data & output wav data   ###
"""

def create_input(choice): 
  # Create a list of 3 usable MIDI paths
  paths = []
  if choice == 'Dance':
    theme = 'dance/'
  else :
    theme = 'sad/'
  for path in range(3):
    dance_random = random.choice(os.listdir("midi_samples/" + theme))
    while dance_random[0] == '.':
      dance_random = random.choice(os.listdir("midi_samples/" + theme)) 
    path = ('midi_samples/'+ theme + dance_random)
    paths.append(path)
  return [
          tf.io.gfile.GFile(fn, 'rb').read()
          for fn in sorted(tf.io.gfile.glob(paths))], theme

# Convert a NoteSequence to midi and the midi to a Wav file
def sequence_to_wav_file(sequence,theme):
  filename = theme[:-1] + '.mid'
  mm.note_sequence_to_midi_file(sequence, filename, None)
  fs = FluidSynth('MuseScore_General.sf2')
  fs.midi_to_audio(filename, theme[:-1] + '.wav')
  return theme[:-1] + '.wav'

"""
###   Extract NoteSequence from random MIDI files  ###
"""

# Convert in NoteSequence and Extract melodies or trio (bass, lead & drums) depending on the theme
def gen_interpolation(input_midi_data,theme):
  input_seqs = [mm.midi_to_sequence_proto(m) for m in input_midi_data]
  if theme == 'sad/':
    # Extract melodies from MIDI files. 
    # This will extract all unique 16-bar melodies using a sliding window with a stride of 1 bar.
    
    extracted_16_mels = []
    for ns in input_seqs:
      extracted_16_mels.extend(
          hierdec_mel_16bar_config.data_converter.from_tensors(
              hierdec_mel_16bar_config.data_converter.to_tensors(ns)[1]))
    return extracted_16_mels

  else :
    # Extract trios from MIDI files. 
    # This will extract all unique 16-bar trios using a sliding window with a stride of 1 bar.

    extracted_trios = []
    for ns in input_seqs:
      extracted_trios.extend(
          hierdec_trio_16bar_config.data_converter.from_tensors(
              hierdec_trio_16bar_config.data_converter.to_tensors(ns)[1]))
    return extracted_trios

"""
###   Generate Interpolation  ###
"""

# Create interpolation between the NoteSequences
def interpolate(model, start_seq, end_seq, num_steps, max_length=32,
                assert_same_length=True, temperature=0.5,
                individual_duration=4.0):
    # Interpolates between a start and end sequence.
    note_sequences = model.interpolate(
      start_seq, end_seq,num_steps=num_steps, length=max_length,
      temperature=temperature,
      assert_same_length=assert_same_length)
    interp_seq = mm.sequences_lib.concatenate_sequences(
      note_sequences, [individual_duration] * len(note_sequences))
    mm.plot_sequence(interp_seq)
    return interp_seq


# Define model parameters to create the final interpolation
def gen_final(extracted_16, theme):
  # Compute the reconstructions and mean
  interp_model = ''
  final_model = mel_16bar_models
  if theme == 'sad/':
    interp_model = "hierdec_mel_16bar"
  else:
    interp_model = "hierdec_trio_16bar"
    final_model = trio_models
  # Define music lenght depending on the size of the extracted Notesequence 
  start = random.randint(0,len(extracted_16))
  end = start
  while start == end :
    end = random.randint(0,len(extracted_16))
  if end < start :
    a = end
    end =start
    start = a
  
  start = extracted_16[start]
  end = extracted_16[end]
  # Generate random outpout filter named temperature for probability prediction 
  temperature = random.randint(1, 16)/10.0
  
  return interpolate(final_model[interp_model], start, end, num_steps=3, max_length=256, individual_duration=32, temperature=temperature), interp_model