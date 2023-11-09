from bark.api import generate_audio
from transformers import BertTokenizer
from bark.generation import SAMPLE_RATE, preload_models, codec_decode, generate_coarse, generate_fine, generate_text_semantic

from scipy.io.wavfile import write as write_wav

def preload():
  # download and load all models
  preload_models(
      text_use_gpu=True,
      text_use_small=False,
      coarse_use_gpu=True,
      coarse_use_small=False,
      fine_use_gpu=True,
      fine_use_small=False,
      codec_use_gpu=True,
      force_reload=False
  )

def get_array(text_prompt, voice_name):
  # generation with more control
  #return generate_audio(text_prompt, history_prompt=voice_name, text_temp=0.7, waveform_temp=0.7)
  x_semantic = generate_text_semantic(
      text_prompt,
      history_prompt=voice_name,
      temp=0.7,
      top_k=50,
      top_p=0.9,
      min_eos_p=.1
  )

  x_coarse_gen = generate_coarse(
      x_semantic,
      history_prompt=voice_name,
      temp=0.7,
      top_k=50,
      top_p=0.90,
  )
  x_fine_gen = generate_fine(
      x_coarse_gen,
      history_prompt=voice_name,
      temp=0.7,
  )

  return codec_decode(x_fine_gen)

def make_file(text_prompt, voice_name, output_file):
  # save audio
  write_wav(output_file, SAMPLE_RATE, get_array(text_prompt, voice_name))
