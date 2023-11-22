import fastapi, howl, murmur

bw = fastapi.FastAPI()

@bw.get("/")
def index():
  return "<html>yay</html>"
