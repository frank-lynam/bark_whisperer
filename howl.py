from scipy.io.wavfile import write as write_wav
import numpy as np

import sys, os, time
import howl_wrapper

def hms(s):
  h = int((s - s % 3600)/3600)
  m = int((s - h*3600 - s % 60)/60)
  s = int(s-((h*60)+m)*60)
  return f"{h:0>2}:{m:0>2}:{s:0>2}"

def fnify(fns):
  return "_".join([x.split('/')[-1].replace(" ", "_").replace(".txt", "") for x in fns if x]).replace("'","").replace('"',"")

def ffmpeg_concat(files, filename, path="howl_output/"):
  files = "\n".join([f"file '{x}'" for x in files])
  with open(path + "files.txt", "w") as fl:
    fl.write(files)
  os.system(f"ffmpeg -loglevel quiet -f concat -y -i {path}files.txt output/{filename}")
  os.unlink(f"{path}files.txt")

def threshold(a, n, th, j=0):
  return len([j:=j+1 if i>th else j-1 if j>0 else j for i in a if j<n])+n

def trim(a, n=4, th=0.01):
  return a[threshold(a,n,th):-threshold(a[::-1],n,th)]

def fade(a, n=4, th=0.01, sample_rate=howl_wrapper.SAMPLE_RATE, fade=0.4):
  # Someday I will replace this with a one-liner =]
  s = threshold(a,n,th)
  e = threshold(a[::-1],n,th)
  fl = int(fade * sample_rate)
  sx = 0 if s < fl else s - fl
  ex = 0 if e < fl else e - fl
  e = len(a) - e
  ex = len(a) - ex
  r = a[s:e]
  if sx != s:
    r = np.concatenate([[x * i / (s-sx) for i, x in enumerate(a[sx:s])], r])
  if ex != e:
    r = np.concatenate([r, [x * (1 - (i / (ex-e))) for i, x in enumerate(a[e:ex])]])
  return r

def preload():
  return howl_wrapper.preload()

def remove_pauses(a, min_pause=0.5, sample_rate=howl_wrapper.SAMPLE_RATE, th=0.01):

  b = [[]]
  n=-1
  for x in a:
    b[-1].append(x)
    n=n+1 if n>-1 and x<th else 0 if x>th else n
    if n>=min_pause * sample_rate:
      b.append([])
      n=-1

  if len(b)>1:
    print(f"Removing {len(b)-1} pauses")
  c = np.concatenate([fade(np.array(x)) for x in b])
  print(f"Rounded off {100*(len(a)-len(c))/len(a):.1f}%")
  return c

def process(infile, voice='en_speaker_6', tags=False, filename=None):

  print(f"\nHaving {voice} read {infile}" + 
    (f" in their {tags} voice" if tags else ""))

  print("\nLoading models...")
  howl_wrapper.preload()

  os.system("mkdir howl_output 2> /dev/null")
  os.system("rm howl_output/* 2> /dev/null")
  write_wav(f"howl_output/00000000.wav", howl_wrapper.SAMPLE_RATE, np.zeros(int(0.5 * howl_wrapper.SAMPLE_RATE)))

  print("\nSynthesizing audio...")
  start_time = time.perf_counter()

  with open(infile) as fl:
    t=fl.read()

  l=[""]
  s=['\n',".","!","?"]
  w=[" ","\t"]
  n=False
  c=True
  for x in t:
    if x in s:
      n=True
      if x=="." and (l[-1][-3:].lower() == "mrs" or l[-1][-2:].lower() in ["mr", "ms"]):
        n=False
    elif n and len(l[-1])>0 and x!='"':
      if l[-1][-1] not in s:
        if l[-1][-1]=='"':
          if l[-1][-2] not in s:
            l[-1]=l[-1][:-1]+"."+'"'
        else:
          l[-1]+="."
      c=True
      n=False
      l.append("")
    if x!="\n" and ((n==False and len(l[-1])>0) or x not in w):
      if c and x!='"':
        c=False
        x=x.upper()
      l[-1]+=x

  if tags:
    if tags == "singing":
      l = [f"♪ " + x + " ♪" for x in l]
    else:
      l = [f"[{tags.upper()}] " + x for x in l]

  for i, x in enumerate(l):
    dt = (time.perf_counter() - start_time)
    eta = dt * len(l) / i if i > 0 else 0
    print(f'\n{hms(dt)}/{hms(eta)}s, {i+1}/{len(l)}: "{x.strip()}"')
    write_wav(f"howl_output/{i+1:0>8}.wav", howl_wrapper.SAMPLE_RATE, remove_pauses(howl_wrapper.get_array(x.strip(), voice)))

  print("\nConcatenating files...")
  if filename == None:
    filename = fnify([voice, infile, tags]) + ".mp3"
  ffmpeg_concat(sorted(os.listdir("howl_output")), filename)
  os.system("rm howl_output/*")
  os.system("rmdir howl_output")

  print (f"\nSaved output/{filename}")
  return "output/" + filename

if __name__=="__main__":
  if len(sys.argv) < 3:
    print("Usage: python howl.py {voice} {text file} [{prepended tag}]")
    print("  Tip: Use the tag 'singing' for singing!")
    exit()
  process(*sys.argv[1:])
