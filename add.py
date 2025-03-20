import qbittorrentapi
import json
import os
from pathlib import Path
from prompt_toolkit import prompt
# instantiate a Client using the appropriate WebUI configuration
conn_info = dict(
    host="127.0.0.1",
    port=8082,
    username="admin",
    password="qwe123",
)
qbt_client = qbittorrentapi.Client(**conn_info)

# the Client will automatically acquire/maintain a logged-in state
# in line with any request. therefore, this is not strictly necessary;
# however, you may want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# if the Client will not be long-lived or many Clients may be created
# in a relatively short amount of time, be sure to log out:
qbt_client.auth_log_out()

# or use a context manager:
with qbittorrentapi.Client(**conn_info) as qbt_client:
    #if qbt_client.torrents_add(urls="...") != "Ok.":
    #    raise Exception("Failed to add torrent.")
    #read file
    base_path = "F:\\test\\"
    json_path = "./Generated/Products/anime_info.json"
    with open(json_path, "r", encoding="utf-8") as f:
        #gen path with titile
        data = json.load(f)
        path = Path(base_path) / data["name"]
        #download file
        all_sub_groups = []
        for i, j in enumerate(data["sub_groups"]):
            item = {
                "index": i,
                "group_name": j["group_name"],
                "episodes": j["episodes"]
            }
            all_sub_groups.append(item)
        msg = "请选择字幕组:\n"
        for i, j in enumerate(all_sub_groups):
            msg += f"{i}: {j['group_name']}\n"
        answer = prompt(msg)
        selected_sub_group = all_sub_groups[int(answer)]
        for k in selected_sub_group["episodes"]:
            url = k["magnet_link"]
            qbt_client.torrents_add(urls=url, save_path=path / selected_sub_group["group_name"])

# display qBittorrent info
    # retrieve and show all torrents
    for torrent in qbt_client.torrents_info():
        print(f"{torrent.hash[-6:]}: {torrent.name} ({torrent.state})")

    # stop all torrents
    #qbt_client.torrents.stop.all()
