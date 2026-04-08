import os, requests

OLLAMA_URL=os.environ.get('OLLAMA_URL','http://127.0.0.1:11434')
OLLAMA_MODEL=os.environ.get('OLLAMA_MODEL','llama3')

class OllamaError(Exception):
  pass

def ping(timeout=2.5):
  try:
    r=requests.get(OLLAMA_URL+'/api/tags', timeout=timeout)
    return r.status_code==200
  except Exception:
    return False

def generate(prompt:str, model:str|None=None, timeout_s:int=120):
  if model is None:
    model=OLLAMA_MODEL
  try:
    r=requests.post(
      OLLAMA_URL+'/api/generate',
      json={'model': model, 'prompt': prompt, 'stream': False},
      timeout=(3.0, float(timeout_s))
    )
    r.raise_for_status()
    j=r.json()
    return j.get('response','')
  except Exception as e:
    raise OllamaError(str(e))
