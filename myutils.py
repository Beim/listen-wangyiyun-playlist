import json, time

import logging.config

logging.basicConfig(
    filename='logging.log',
    level=logging.CRITICAL,
    format='%(asctime)s [%(threadName)s] [%(name)s] [%(levelname)s] %(filename)s[line:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

with open('./config.json', 'r') as f:
  config = json.load(f)
  uid = config['uid']
  port = config['port']

class Util:
  @staticmethod
  def get_timef(localtime: time.localtime = None):
    if localtime is None:
      localtime = time.localtime()
    return time.strftime("%Y-%m-%d-%H-%M-%S", localtime)
  