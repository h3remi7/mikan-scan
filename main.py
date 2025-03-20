import qbittorrentapi

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
    u = "magnet:?xt=urn:btih:f442fe3bcb195f920bf2a0c7e93fea22e39d4d39&tr=http%3a%2f%2ft.nyaatracker.com%2fannounce&tr=http%3a%2f%2ftracker.kamigami.org%3a2710%2fannounce&tr=http%3a%2f%2fshare.camoe.cn%3a8080%2fannounce&tr=http%3a%2f%2fopentracker.acgnx.se%2fannounce&tr=http%3a%2f%2fanidex.moe%3a6969%2fannounce&tr=http%3a%2f%2ft.acg.rip%3a6699%2fannounce&tr=https%3a%2f%2ftr.bangumi.moe%3a9696%2fannounce&tr=udp%3a%2f%2ftr.bangumi.moe%3a6969%2fannounce&tr=http%3a%2f%2fopen.acgtracker.com%3a1096%2fannounce&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce"
    qbt_client.torrents_add(urls=u, save_path="F:\\test", is_paused=False)
    #read file
    base_path = "F:\\test\\"
    with open("F:\\test\\anime_info.json", "r") as f:
        #gen path with titile
        data = json.load(f)
        for i in data["anime"]:
            path = base_path + i["title"]
            os.makedirs(path, exist_ok=True)
            #download file
            for j in i["files"]:
                url = j["url"]
                r = requests.get(url)
        data = json.load(f)
    print(data)

# display qBittorrent info
    print(f"qBittorrent: {qbt_client.app.version}")
    print(f"qBittorrent Web API: {qbt_client.app.web_api_version}")
    for k, v in qbt_client.app.build_info.items():
        print(f"{k}: {v}")

    # retrieve and show all torrents
    for torrent in qbt_client.torrents_info():
        print(f"{torrent.hash[-6:]}: {torrent.name} ({torrent.state})")

    # stop all torrents
    qbt_client.torrents.stop.all()
