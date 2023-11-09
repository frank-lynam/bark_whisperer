# This also requires other dependencies to get working, like hubert

from hubert.hubert_manager import HuBERTManager
from hubert.pre_kmeans_hubert import CustomHubert
from hubert.customtokenizer import CustomTokenizer

from bark.api import generate_audio
from bark.generation import SAMPLE_RATE, preload_models, codec_decode
from bark.generation import generate_coarse, generate_fine, generate_text_semantic
from bark.generation import load_codec_model, generate_text_semantic

from encodec.utils import convert_audio
from scipy.io.wavfile import write as write_wav
from transformers import BertTokenizer

import torchaudio
import torch
import numpy as np

import sys, os


print ("Cloning script for bark")
print ("A reference file between 60-90 seconds seems most stable. Gotta have clean starts and stops.")


if len(sys.argv) < 2:
  print("Usage: python do_clone.py [{audio file name}] {voice name} ")
  print("Given one parameter, it will look for the audio file 'voice_ref/{voice_name}.wav'")
  exit()

device = 'cuda'
model = load_codec_model(use_gpu=True if device == 'cuda' else False)

hubert_manager = HuBERTManager()
hubert_manager.make_sure_hubert_installed()
hubert_manager.make_sure_tokenizer_installed()


print ("Loading hubert:", int(100*torch.cuda.mem_get_info()[0]/torch.cuda.mem_get_info()[1]))
hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)

print("Loading tokenizer:", int(100*torch.cuda.mem_get_info()[0]/torch.cuda.mem_get_info()[1]))
tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)  

audio_filepath = "voice_ref/" + sys.argv[1] + ".wav"
print("Loading audio:",int(100* torch.cuda.mem_get_info()[0]/torch.cuda.mem_get_info()[1]))
wav, sr = torchaudio.load(audio_filepath)
wav = convert_audio(wav, sr, model.sample_rate, model.channels)
wav = wav.to(device)

print("Loading semantic vectors:", int(100*torch.cuda.mem_get_info()[0]/torch.cuda.mem_get_info()[1]))
semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
print("Loading semantic tokens:", int(100*torch.cuda.mem_get_info()[0]/torch.cuda.mem_get_info()[1]))
semantic_tokens = tokenizer.get_token(semantic_vectors)

print("Extracting codes:", int(100*torch.cuda.mem_get_info()[0]/torch.cuda.mem_get_info()[1]))
with torch.no_grad():
    encoded_frames = model.encode(wav.unsqueeze(0))
codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze() 

print("Moving data to cpu:", int(100*torch.cuda.mem_get_info()[0]/torch.cuda.mem_get_info()[1]))
codes = codes.cpu().numpy()
semantic_tokens = semantic_tokens.cpu().numpy()

voice_name = sys.argv[-1] 
output_path = 'bark/assets/prompts/' + voice_name + '.npz'
np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)

print (f"Saved {voice_name}.npz")

yn = input("Fine tune to a stable variant? [y/n] ")
if yn.lower().startswith("n"):
  exit()


text_prompt = "A song not for now, you need not put-stay. A tune for the was can be sung for today? The notes of the does-not will sound like the does... Today you can sing for the will-be that was!"

print ("Loading generation models")

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

while True:

  px = input("Enter optional variant prefix: [blank for none] ").strip().upper()
  print ("Generating variant...")
  
  x_semantic = generate_text_semantic(
      ("[" + px + "] " if len(px)>0 else "") + text_prompt,
      history_prompt=voice_name,
      temp=0.7,
      top_k=50,
      top_p=0.95,
  )

  x_coarse_gen = generate_coarse(
      x_semantic,
      history_prompt=voice_name,
      temp=0.7,
      top_k=50,
      top_p=0.95,
  )
  x_fine_gen = generate_fine(
      x_coarse_gen,
      history_prompt=voice_name,
      temp=0.5,
  )
  audio_array = codec_decode(x_fine_gen)

  filepath = "./output/clone_sample.wav" 
  write_wav(filepath, SAMPLE_RATE, audio_array)
  os.system("aplay output/clone_sample.wav")

  yn = input("Like it? [y/n] ")
  if yn.lower().startswith("y"):
    break

os.unlink(filepath)
np.savez(output_path, fine_prompt=x_fine_gen, coarse_prompt=x_coarse_gen, semantic_prompt=x_semantic)

print (f"Saved {voice_name}.npz")
