print("Starting bark whisperer...")

import fastapi, howl, murmur, typing, os, base64, json

bw = fastapi.FastAPI()
howl.preload()

@bw.get("/")
async def index():
  with open("index.html") as fl:
    page = fl.read()
  return fastapi.responses.HTMLResponse(page)

@bw.post("/upload")
async def upload(file: str = fastapi.Body("")):
  id = max([int(x) for x in os.listdir("input") if x.isdigit()]) + 1
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
  with open(f"text/{id}", "w") as fl:
    fl.write(text)
  return text

@bw.get("/tts/{id}")
async def tts(id):
  howl.process(f"text/{id}", filename=f"{id}.ogg")
  os.system(f"mv output/{id}.ogg output/{id}")
  return fastapi.responses.FileResponse(f"output/{id}", media_type='audio/ogg')

@bw.get("/output/{id}")
async def output(id):
  return fastapi.responses.FileResponse(f"output/{id}", media_type='audio/ogg')

@bw.get("/input/{id}")
async def input(id):
  return fastapi.responses.FileResponse(f"input/{id}", media_type='audio/ogg')
  
