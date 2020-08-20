import json, os, time

from musicbox.NEMbox.api import NetEase, Parse
from myutils import uid, Util

api = NetEase()

def fetch_playlist() -> (object, object):
  """
  playlist 是数组，里面每一个对象有id, updateTime, creator.userId

  """
  timef = Util.get_timef()
  data_dir = './data/%s' % timef
  os.mkdir(data_dir)

  playlist_original = api.user_playlist(uid)
  playlist = []
  for pl in playlist_original:
    if pl['creator']['userId'] == uid:
      playlist.append(pl)

  playlist_obj = {}
  for pl in playlist:
    playlist_obj[pl['id']] = pl
  with open('%s/playlist.json' % (data_dir), 'w', encoding='utf-8') as f:
    json.dump(playlist_obj, f, ensure_ascii=False)
  details = {}
  for pl in playlist:
    details[pl['id']] = api.playlist_detail(pl['id'])
  with open('%s/detail.json' % (data_dir), 'w', encoding='utf-8') as f:
    json.dump(details, f, ensure_ascii=False)
  return playlist_obj, details

def compare_playlist(new_timef: str, old_timef: str):
  new_playlist_path = './data/%s/playlist.json' % new_timef
  new_details_path = './data/%s/detail.json' % new_timef
  old_playlist_path = './data/%s/playlist.json' % old_timef
  old_details_path = './data/%s/detail.json' % old_timef
  with open(new_playlist_path, 'r', encoding='utf-8') as f:
    new_playlist = json.load(f)
  with open(old_playlist_path, 'r', encoding='utf-8') as f:
    old_playlist = json.load(f)
  with open(new_details_path, 'r', encoding='utf-8') as f:
    new_details = json.load(f)
  with open(old_details_path, 'r', encoding='utf-8') as f:
    old_details = json.load(f)
  
  # playlist 的变化
  new_added_playlist = []
  new_removed_playlist = []
  updated_playlist = []
  recent_listen_playlist = []
  new_playlist_ids = set()
  old_playlist_ids = set()
  for plid in new_playlist:
    new_playlist_ids.add(plid)
  for plid in old_playlist:
    old_playlist_ids.add(plid)
  new_added_playlist = list(new_playlist_ids - old_playlist_ids)
  new_removed_playlist = list(old_playlist_ids - new_playlist_ids)
  for plid in new_playlist_ids.intersection(old_playlist_ids):
    if new_playlist[plid]['updateTime'] != old_playlist[plid]['updateTime']:
      updated_playlist.append(plid)
    if new_playlist[plid]['playCount'] != old_playlist[plid]['playCount']:
      recent_listen_playlist.append(plid)
  
  new_added_playlist_info = {}
  """
  {
    "<playlist_id>": {
      "id": "",
      "name": "",
      "updateTime": "",
      "playCount": "",
      "creator": {},
      "detail": []
    }
  }
  """
  new_removed_playlist_info = {} # 格式同new_added_playlist_info
  updated_playlist_info = {}
  """
  {
    "<playlist_id">: {
      "id": "",
      "name": "",
      "updateTime": "",
      "playCount": "",
      "creator": {},
      "added_detail": [],
      "removed_detail": [],
    }
  }
  """
  recent_listen_playlist_info = {}
  """
  {
    "<playlist_id>": {
      "id": "",
      "name": "",
      "updateTme": "",
      "playCount": "",
      "creator": {},
      "playCount": "",
    }
  }
  """
  for plid in new_added_playlist:
    obj = {
      'id': plid,
      'name': new_playlist[plid]['name'],
      # 'coverImgUrl': new_playlist[plid]['coverImgUrl'],
      'updateTime': Util.get_timef(time.localtime(new_playlist[plid]['updateTime'] / 1000)),
      "playCount": new_playlist[plid]['playCount'],
      'creator': new_playlist[plid]['creator']['nickname'],
      # 'detail': new_details[plid],
    }
    new_added_playlist_info[plid] = obj
  for plid in new_removed_playlist:
    obj = {
      'id': plid,
      'name': old_playlist[plid]['name'],
      # 'coverImgUrl': old_playlist[plid]['coverImgUrl'],
      'updateTime': Util.get_timef(time.localtime(old_playlist[plid]['updateTime'] / 1000)),
      "playCount": new_playlist[plid]['playCount'],
      'creator': old_playlist[plid]['creator']['nickname'],
      # 'detail': old_details[plid],
    }
    new_removed_playlist_info[plid] = obj
  for plid in updated_playlist:
    obj = {
      'id': plid,
      'name': new_playlist[plid]['name'],
      # 'coverImgUrl': new_playlist[plid]['coverImgUrl'],
      'updateTime': Util.get_timef(time.localtime(new_playlist[plid]['updateTime'] / 1000)),
      "playCount": new_playlist[plid]['playCount'],
      'creator': new_playlist[plid]['creator']['nickname'],
      # 'detail': new_details[plid],
      'added_detail': [],
      'removed_detail': []
    }
    new_detail_ids = set()
    old_detail_ids = set()
    new_detail_id2obj = {}
    old_detail_id2obj = {}
    for detail in new_details[plid]:
      new_detail_ids.add(detail['id'])
      new_detail_id2obj[detail['id']] = detail
    for detail in old_details[plid]:
      old_detail_ids.add(detail['id'])
      old_detail_id2obj[detail['id']] = detail
    for did in list(new_detail_ids - old_detail_ids):
      obj['added_detail'].append({
        'name': new_detail_id2obj[did]['name'],
        'id': new_detail_id2obj[did]['id'],
        'ar': new_detail_id2obj[did]['ar'],
      })
    for did in list(old_detail_ids - new_detail_ids):
      obj['removed_detail'].append({
        'name': old_detail_id2obj[did]['name'],
        'id': old_detail_id2obj[did]['id'],
        'ar': old_detail_id2obj[did]['ar']
      })
    updated_playlist_info[plid] = obj
  for plid in recent_listen_playlist:
    obj = {
      'id': plid,
      'name': new_playlist[plid]['name'],
      # 'coverImgUrl': new_playlist[plid]['coverImgUrl'],
      'updateTime': Util.get_timef(time.localtime(new_playlist[plid]['updateTime'] / 1000)),
      "playCount": new_playlist[plid]['playCount'],
      'creator': new_playlist[plid]['creator']['nickname'],
      'newPlayCount': new_playlist[plid]['playCount'] - old_playlist[plid]['playCount'],
    }
    recent_listen_playlist_info[plid] = obj
  return updated_playlist_info, new_added_playlist_info, new_removed_playlist_info, recent_listen_playlist_info
    
def read_timefs():
  timefs = os.listdir('./data')
  timefs.sort()
  timefs.reverse()
  return timefs


if __name__ == '__main__':
  res = api.user_playlist(111365099)
  res = res[0]
  with open('./temp.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=4, ensure_ascii=False)
  print(Util.get_timef(time.localtime(res['trackUpdateTime']/1000)))
  print(Util.get_timef(time.localtime(res['updateTime'] / 1000)))
  print(Util.get_timef(time.localtime(res['trackNumberUpdateTime'] / 1000)))
  print(res['playCount'])
  print(res['trackCount'])

  # fetch_playlist()
  # timefs = read_timefs()
  # if len(timefs) >= 2:
  #   updated_playlist_info, new_added_playlist_info, new_removed_playlist_info = compare_playlist(timefs[0], timefs[1])
  #   print(updated_playlist_info, new_added_playlist_info, new_removed_playlist_info)
  #   with open('./updated_playlist_info', 'w', encoding='utf-8') as f:
  #     json.dump(updated_playlist_info, f, ensure_ascii=False, indent=4)
  #   with open('./new_added_playlist_info', 'w', encoding='utf-8') as f:
  #     json.dump(new_added_playlist_info, f, ensure_ascii=False, indent=4)
  #   with open('./new_removed_playlist_info', 'w', encoding='utf-8') as f:
  #     json.dump(new_removed_playlist_info, f, ensure_ascii=False, indent=4)
  