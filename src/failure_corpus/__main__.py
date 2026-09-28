import json,sys
from .core import parse,dedupe
for f in dedupe(parse(open(sys.argv[1]).read())): print(json.dumps(f.as_dict(),sort_keys=True))
