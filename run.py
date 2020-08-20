from concurrent import futures
import json
import logging

from flask import Flask
from apscheduler.schedulers.blocking import BlockingScheduler
import shutil

import api
from myutils import port
from mail import send_email

app = Flask(__name__)

def check_update():
  api.fetch_playlist()
  timefs = api.read_timefs()
  if len(timefs) < 2:
    return
  updated_playlist_info, new_added_playlist_info, new_removed_playlist_info, recent_listen_playlist_info = api.compare_playlist(timefs[0], timefs[1])
  if len(updated_playlist_info) > 0 or len(new_added_playlist_info) > 0 or len(new_removed_playlist_info) > 0 or len(recent_listen_playlist_info) > 0:
    with open('./updated_playlist_info', 'w', encoding='utf-8') as f:
      json.dump(updated_playlist_info, f, ensure_ascii=False, indent=4)
    with open('./new_added_playlist_info', 'w', encoding='utf-8') as f:
      json.dump(new_added_playlist_info, f, ensure_ascii=False, indent=4)
    with open('./new_removed_playlist_info', 'w', encoding='utf-8') as f:
      json.dump(new_removed_playlist_info, f, ensure_ascii=False, indent=4)
    with open('./recent_listen_playlist_info', 'w', encoding='utf-8') as f:
      json.dump(recent_listen_playlist_info, f, ensure_ascii=False, indent=4)
    content = "更新歌单: \n%s\n\n最近听歌: \n%s\n\n创建歌单: \n%s\n\n删除歌单: \n%s" % (
      json.dumps(updated_playlist_info, ensure_ascii=False, indent=4),
      json.dumps(recent_listen_playlist_info, ensure_ascii=False, indent=4),
      json.dumps(new_added_playlist_info, ensure_ascii=False, indent=4),
      json.dumps(new_removed_playlist_info, ensure_ascii=False, indent=4),
    )
    title = "[tz-playlist-update] from %s to %s" % (timefs[1], timefs[0])
    # print()
    logging.critical('sent email: %s' % title)
    send_email(title, content)
  else:
    # print()
    logging.critical('no update, remove dir ./data/%s' % timefs[0])
    shutil.rmtree('./data/%s' % timefs[0])
    

if __name__ == '__main__':
  def schedule():
    scheduler = BlockingScheduler()
    for idx in range(0, 24, 2):
      scheduler.add_job(check_update, 'cron', day_of_week='0-6', hour=idx, minute=1)
    # scheduler.add_job(check_update, 'cron', day_of_week='0-6', hour=11, minute=0)
    # scheduler.add_job(check_update, 'cron', day_of_week='0-6', hour=19, minute=0)
    # scheduler.add_job(check_update, 'cron', day_of_week='0-6', hour=23, minute=58)
    print('start scheduler')
    scheduler.start()
  
  check_update()
  schedule()

  # executor = futures.ThreadPoolExecutor(max_workers=2)
  # executor.submit(schedule)
  # app.run('0.0.0.0', port)
  
  