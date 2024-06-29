print("Starting bark whisperer...")

import fastapi, howl, murmur, sunshine, typing, os, base64, json

bw = fastapi.FastAPI()
howl.preload()

@bw.get("/")
async def index():
  with open("index.html") as fl:
    page = fl.read()
  return fastapi.responses.HTMLResponse(page)

@bw.get("/favicon.png")
async def favicon():
  return fastapi.responses.FileResponse("favicon.png")

@bw.post("/upload")
async def upload(file: str = fastapi.Body("")):
  id = [int(x) for x in os.listdir("input") if x.isdigit()]
  if len(id)==0:
    id = 0
  else:
    id=max(id)
  
  with open(f"input/{id}", "wb") as fl:
    fl.write(bytes(json.loads("["+str(base64.b64decode(file))[5:-1] + "]")))
  os.system(f"ffmpeg -i input/{id} input/{id}.wav")
  os.system(f"mv input/{id}.wav input/{id}")
  return id

@bw.get("/stt/{id}")
async def stt(id):
  text = murmur.listen(f"input/{id}")
  with open(f"text/{id}", "w") as fl:
    fl.write(text)
  return text

@bw.get("/text/{id}")
async def text(id):
  with open(f"text/{id}") as fl:
    txt = fl.read()
  return txt

@bw.get("/langs")
async def langs():
  return sunshine.langs()

@bw.get("/tts/{id}")
async def tts(id, tags=False, lang="en"):
  with open(f"text/{id}") as fl:
    text = fl.read().strip()
  for _ in range(10):
    new_text = sunshine.desert(f"Translate everything here to {sunshine.langs()[lang]}: {text}")
    if new_text=="":
      break
  if new_text=="":
    text="Translation error translating: " + text
  else:
    text=new_text

  with open(f".howl.tmp.{id}", "w") as fl:
    fl.write(text)
  howl.process(f".howl.tmp.{id}", filename=f"{id}.ogg", tags=tags, voice=f"{lang}_speaker_6")
  os.system(f"rm -rf .howl.tmp.{id}")
  os.system(f"mv output/{id}.ogg output/{id}")
  return fastapi.responses.FileResponse(f"output/{id}", media_type='audio/ogg')

@bw.get("/output/{id}")
async def output(id):
  return fastapi.responses.FileResponse(f"output/{id}", media_type='audio/ogg')

@bw.get("/input/{id}")
async def input(id):
  return fastapi.responses.FileResponse(f"input/{id}", media_type='audio/ogg')
  
