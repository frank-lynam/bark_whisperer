from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("translate/")
model = T5ForConditionalGeneration.from_pretrained("translate/", device_map="auto")

def langs():
  return {"en":"English", "fr":"French", "it":"Italian", "de":"German", 
    "pl":"Polish", "pt":"Portuguese", "es":"Spanish", "tr":"Turkish"}

# Have TTS, but no unicode in flan: "hi":"Hindi", "ja":"Japanese", "ko":"Korean", "ru":"Russian", "zh":"Chinese"

def desert(input_text):
  input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to("cuda")
  outputs = model.generate(input_ids)
  return tokenizer.decode(outputs[0]).split(">")[1].split("<")[0].strip()

if __name__=="__main__":
  import sys
  print (desert(sys.argv[1]))
