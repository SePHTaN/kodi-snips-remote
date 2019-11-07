#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import requests
import re
import time
kodi_url = ''
debuglevel = 1 # 0= snips subscriptions; 1= function call; 2= debugs; 3=higher debug
playlist_size =20
def ausgabe(text,mode):
    '''
    main function name -mode= 1
    debugs -mode= >=2
     - kodi function -mode= 1
       -- snips subscription -mode= 0
    '''
    ausgabe=""
    if mode < 2:
        ausgabe = " - "
    if mode >= debuglevel:
        print((ausgabe + str(text)))
    return
def send(g_data,isfilter=0,all_data="",caller=""): #added caller=""  for JSON-String debug
    headers = {
            'Content-type': 'application/json',
        }
    if all_data =="":
        data_head = '{"id":"160","jsonrpc":"2.0",'
        data_end = '}'
        data = data_head + g_data + data_end
    else:
        data = all_data
    try:
        ausgabe(caller+': '+data,1)
        response = requests.post(kodi_url, headers=headers, data=data)
        json_obj= response.text
        ausgabe('Send: Response JSON-OBJ = ' + json_obj,2) #added "Send JSON-OBJ = " +
        json_data = json.loads(json_obj)
        if all_data != "":
            return json_data
        for item in json_data:
            if item == 'result':
                #ausgabe('send is good',2)
                json_data = json_data['result']
                if isfilter == 0:
                    filter_dict(json_data)
                return(json_data)
            elif item == 'error':
                ausgabe('send is bad',2)
                ausgabe('data: '+data,2)
                ausgabe(json_data,2)
                return
    except:
        ausgabe('server nicht erreichbar: '+kodi_url ,2)
        return
    return
def check_connectivity():
    #ausgabe('check_connectivity',1)
    data_method= '"method":"JSONRPC.Ping"'
    data_prop = ',"params":{}'
    data = data_method + data_prop
    json_data=send(data,1,'','check_connectivity')
    return json_data
def filter_dict(d):
    #cause snips get confused with special characters this will replace all special chars with ' '
    #ausgabe('filter_dict',1)
#    for key, value in d.items():
    for key, value in list(d.items()):
        if isinstance(value, dict):
            d[key] = filter_dict(value)
        elif isinstance(value, list):
            d[key] = [filter_dict(l) for l in value]
        else:
            d[key]=re.sub('[^A-Za-z0-9 ]+', ' ', str(value))
    return d
def get_movies():
    #ausgabe('get_movies',1)
    data_method= '"method":"VideoLibrary.GetMovies"'
    data_prop = ',"params":{"properties":["title"],"sort":{"method":"none","order":"ascending"}}'
    data = data_method + data_prop
    json_data=send(data,0,'','get_movies')
    #ausgabe('get_movies - data= ' + data + 'jd-movies=' + json_data['movies'],1)
    return(json_data['movies'])
def get_shows():
    #ausgabe('get_shows',1)
    data_method= '"method":"VideoLibrary.GetTVShows"'
    data_prop = ',"params":{"properties":["title"],"sort":{"method":"none","order":"ascending"}}'
    data = data_method + data_prop
    json_data=send(data,0,'','get_shows')
    #ausgabe('get_shows - data= ' + data + 'jd-tvshows=' + json_data['tvshows'],1)
    return(json_data['tvshows'])
def get_tv_shows(tag):
    #ausgabe('get_tv_shows',1)
    data_method= '"method":"VideoLibrary.GetTVShows"'
    data_prop = ',"params":{"properties":["tag"],"sort":{"method":"none","order":"ascending"},'\
                '"filter":{"tag":"'+tag+'"}}'
    data = data_method + data_prop
    json_data=send(data,1,'','get_tv_shows')
    return(json_data['tvshows'])
def get_tv_shows_episodeids(tupel):
    #ausgabe('get_tv_shows_id',1)
    num=0
    data = "["
    for item in tupel:
        data_head = '{"id":"'+str(item)+'","jsonrpc":"2.0",' # falsch? prüfen
        data_method= '"method":"VideoLibrary.GetEpisodes"'
        data_prop = ',"params":{"tvshowid":'+str(item)+','\
                    '"properties":[],'\
                    '"sort": { "order": "ascending", "method": "label"}}}'
                    #'"limits":{"end":20,"start":0}}}'
        data = data + data_head + data_method + data_prop
        if num+1 < len(tupel):
            data = data + ', '
        num =num+1
    data = data + "]"
    json_data=send("",1,data,'get_tv_shows_id')
    #ausgabe(json_data,3)
    return(json_data)
#test = [2, 9, 15, 19, 22, 39, 48, 52, 53, 65, 66, 68, 69, 70, 71, 72]
#get_tv_shows_episodeids(test)
def get_genre():
    #ausgabe('get_genre',1)
    data_method= '"method":"AudioLibrary.GetGenres"'
    data_prop = ',"params":{"properties":["title"],"sort":{"method":"none","order":"ascending"}}'
    data = data_method + data_prop
    json_data=send(data,0,'','get_genre')
    #ausgabe('get_genre - data= ' + data + 'jd-genres=' + json_data['genres'],1)
    return(json_data['genres'])
def get_artists():
    #ausgabe('get_artists',1)
    data_method= '"method":"AudioLibrary.GetArtists"'
    data_prop = ',"params":{"albumartistsonly":false,"properties":[],"limits":{"start":0},"sort":{"method":"label","order":"ascending","ignorearticle":true}}'
    data = data_method + data_prop
    json_data=send(data,0,'','get_artists')
    #ausgabe('get_artists - data= ' + data + 'jd-artists=' + json_data['artists'],1)
    return(json_data['artists'])
#def get_songtitles():
#    ausgabe('get_songtitles',1)
#    data_method= '"method":"AudioLibrary.GetSongs"'
#    data_prop = ',"params":{"properties":["title"],"limits":{"start":0},"sort":{"method":"title","order":"ascending","ignorearticle":true}}'
#    data = data_method + data_prop
#    json_data=send(data)
#    return(json_data['songs'])
def get_albums():
    #ausgabe('get_albums',1)
    data_method= '"method":"AudioLibrary.GetAlbums"'
    data_prop = ',"params":{"properties":["title"],"limits":{"start":0},"sort":{"method":"title","order":"ascending","ignorearticle":true}}'
    data = data_method + data_prop
    json_data=send(data,0,'','get_albums')
    #ausgabe('get_albums - data= ' + data + 'jd-albums=' + json_data['albums'],1)
    return(json_data['albums'])
#def get_songs_by(filterkey,filtervalue):
#    ausgabe('get_songs_by',1)
#    data_method= '"method":"AudioLibrary.GetSongs"'
#    data_prop = ',"params":{"properties":["title","albumid"],'\
#                '"limits":{"start":0},"sort":{"method":"track","order":"ascending","ignorearticle":true},'\
#                '"filter":{"'+filterkey+'":'+filtervalue+'}}'
#    data = data_method + data_prop
#    json_data=send(data)
#    return(json_data['songs'])
def find_title_id(titlename,searchkey,id_slot_name,json_data):
    #ausgabe('find_title_id',1)
    titleid=0
    for item in json_data:
        if item[searchkey].lower()==titlename.lower():
            titleid = item[id_slot_name]
            break
    ausgabe(' find_title_id: TitleId:"{0}"'.format(titleid),1,)
    return(titleid)
def find_title(titlename,json_data):
    #ausgabe('find_title',1)
    title_found =[]
    for item in json_data:
        if titlename.lower() in item['label'].lower():
            title_found = title_found+ [item['label']]
    ausgabe(' find_title: "{0}"'.format(title_found),1)
    return(title_found)
def get_episodes_unseen(id):
    #ausgabe('get_episodes_unseen',1)
    data_method= '"method":"VideoLibrary.GetEpisodes"'
    data_prop = ',"params":{"tvshowid":'+str(id)+',' \
                '"filter": {"field": "playcount", "operator": "lessthan", "value": "1"},' \
                '"properties":["title"], ' \
                '"sort": { "order": "ascending", "method": "label" }'\
                '}'
    data = data_method + data_prop
    json_data=send(data,1,'','get_episodes_unseen')
    #ausgabe('get_episodes_unseen - data= ' + data + 'jd-epi-uns=' + json_data,1)
    return(json_data)
def get_episodes_all(id):
    #ausgabe('add_episodes_all',1)
    data_method= '"method":"VideoLibrary.GetEpisodes"'
    data_prop = ',"params":{"tvshowid":'+str(id)+','\
                '"properties":["title"],'\
                '"sort": { "order": "ascending", "method": "label" }'\
                '}'
    data = data_method + data_prop
    json_data=send(data,1,'','get_episodes_all')
    #ausgabe('add_episodes_all - data= ' + data + 'jd-epi-all=' + json_data,1)
    return(json_data)
def add_playlist(playlist,playlistid):
    ausgabe("add_playlist",1)
    clear_playlist(playlistid)
    data_method= '"method":"Playlist.Add"'
    data_prop = ',"params":{"playlistid":'+str(playlistid)+',"item": {"recursive": true,"directory": "special://profile/playlists/'+playlist+'"}}'
    data = data_method + data_prop
    send(data,1)
    return
def insert_playlist(tupel,types,playlistid):
    clear_playlist(playlistid)
    ausgabe('insert_playlist',1)
    num=0
    data = "["
    for item in tupel:
        data_head = '{"id":"'+str(num+100)+'","jsonrpc":"2.0",'
        data_method= '"method":"Playlist.Insert"'
        data_prop = ',"params":['+str(playlistid)+','+str(num)+',{"'+types+'":'+str(item)+'}]}'
        data = data + data_head + data_method + data_prop
        if num+1 == playlist_size:
            break
        if num+1 < len(tupel):
            data = data + ', '
        num =num+1
    data = data + "]"
    send("",1,data)
    return
def clear_playlist(playlistid):
    ausgabe('clear_playlist',1)
    #ausgabe(playlistid,2)
    data_method = '"method":"Playlist.Clear"'
    data_prop = ',"params":{"playlistid":'+str(playlistid)+'}'
    data = data_method + data_prop
    #ausgabe(data,2)
    send(data,1)
    return
def get_active_player():
    #ausgabe('get_active_player',1)
    data_method= '"method":"Player.GetActivePlayers"'
    data_prop = ',"params":{}'
    data = data_method + data_prop
    active_json = send(data,1,'','get_active_player')
    #print('Result:',active_json)
    if active_json != [] and active_json:
        return(active_json[0])
    else:
        return(active_json)
def get_properties():
    #ausgabe('get_properties',1)
    player_id = get_active_player()
    if player_id:
        #ausgabe('player_id:"{0}"'.format(player_id),1)
        data_method= '"method":"Player.GetProperties"'
        data_prop = ',"params":['+str(player_id['playerid'])+',["playlistid","speed","position","totaltime",'\
                   '"time","percentage","shuffled","repeat","canrepeat","canshuffle",'\
                   '"canseek","partymode"]]'
        data = data_method + data_prop
        json = send(data,1,'','get_properties')
        return(json)
    return
def get_running_state():
    ausgabe('get_running_state',1)
    state = 0
    json_state = get_properties()
    if json_state:
        if json_state['speed'] == 1:
            state=1
    return state
def start_play(playlistid):
    ausgabe('play',1)
    data_method = '"method":"Player.Open"'
    data_prop = ',"params":{"item":{"position":0,"playlistid":'+str(playlistid)+'}}'
    data = data_method + data_prop
    send(data,1)
    return
#def play_pause():
#    ausgabe('play_pause',1)
#    json_data = get_active_player()
#    if json_data != [] and json_data:
#        data_method= '"method":"Player.PlayPause"'
#        data_prop = ',"params":['+str(json_data['playerid'])+',"toggle"]'
#        data = data_method + data_prop
#        send(data,1)
#    return
def resume():
    #ausgabe('resume',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.PlayPause"'
        data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+',"play":true}'
        data = data_method + data_prop
        send(data,1,'','resume')
    return
def pause():
    #ausgabe('pause',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.PlayPause"'
        data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+',"play":false}'
        data = data_method + data_prop
        send(data,1,'','pause')
    return
def stop():
    #ausgabe('stop',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.Stop"'
        data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+'}'
        data = data_method + data_prop
        send(data,1,'','stop')
    return
def partymode():
    #ausgabe('partymode',1)
    #json_data = get_active_player()
    #if json_data != [] and json_data:
    data_method= '"method":"Player.SetPartymode"'
    #data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+',"partymode":true}'
    data_prop = ',"params":{"playerid":1,"partymode":true}'
    data = data_method + data_prop
    send(data,1,'','partymode')
    return
def partymode_playlist():
    #ausgabe('partymode_playlist',1)
    #json_data = get_active_player()
    #if json_data != [] and json_data:
    data_method= '"method":"Player.Open"'
    data_prop = ',"params":{"item":{"partymode":"music"}}'
    data = data_method + data_prop
    send(data,1,'','partymode_playlist')
    return
def subtitles(state):
    #ausgabe('subtitles',1)
    setstate = "off"
    if state == "true":
        setstate = "on"
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.SetSubtitle"'
        data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+',"subtitle":"'+setstate+'"}'
        data = data_method + data_prop
        send(data,1,'','subtitles')
    return
def shuffle(state):
    #ausgabe("shuffle",1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.SetShuffle"'
        data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+',"shuffle":'+state+'}'
        data = data_method + data_prop
        send(data,1,'','shuffle')
    return
def next_media():
    #ausgabe('next_media',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.GoTo"'
        data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+',"to":"next"}'
        data = data_method + data_prop
        send(data,1,'','next_media')
    return
def previous_media():
    #ausgabe('previous_media',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Player.GoTo"'
        data_prop = ',"params":{"playerid":'+str(json_data['playerid'])+',"to":"previous"}'
        data = data_method + data_prop
        send(data,1,'','previous_media')
    return
def lauter(schritte):
    ausgabe('lautstärke_hoch',1)
    schritte = int(schritte)
    if schritte > 10:
        schritte = 10
    data_method= '"method":"Application.SetVolume"'
    data_prop = ',"params":{"volume":"increment"}'
    data = data_method + data_prop
    while schritte > 0:
        schritte = schritte -1
        send(data,1,'','lauter')
        time.sleep(.120)
    return
def leiser(schritte):
    ausgabe('lautstärke_runter',1)
    schritte = int(schritte)
    if schritte > 10:
        schritte = 10
    data_method= '"method":"Application.SetVolume"'
    data_prop = ',"params":{"volume":"decrement"}'
    data = data_method + data_prop
    while schritte > 0:
        schritte = schritte -1
        send(data,1,'','leiser')
        time.sleep(.120)
    return
def volume(vol):
    #ausgabe('lautstärke_setzen',1)
    vol = float(vol)*100
    vol= int(vol)
    #json_data = get_active_player()
    data_method= '"method":"Application.SetVolume"'
    data_prop = ',"params":{"volume":'+str(vol)+'}'
    data = data_method + data_prop
    send(data,1,'','volume')
    return
def mute():
    #ausgabe('lautstärke_an-aus',1)
    json_data = get_active_player()
    if json_data != [] and json_data:
        data_method= '"method":"Application.SetMute"'
        data_prop = ',"params":{"mute":"toggle"}'
        data = data_method + data_prop
        send(data,1,'','mute')
    return
def get_gui():
    data_method= '"method":"GUI.GetProperties"'
    data_prop = ',"params":{"properties":["currentwindow","currentcontrol"]}'
    data = data_method + data_prop
    window = send(data,1)
    return(window['currentwindow'])
def introspect():
    data_method= '"method":"JSONRPC.Introspect"'
    data_prop = ', "params": { "filter": { "id": "GUI.ActivateWindow", "type": "method" } }'
    data = data_method + data_prop
    ausgabe(send(data,1),3)
    return
def show_notification(text):
    data_method= '"method":"GUI.ShowNotification"'
    data_prop = ',"params":{"title":"Notification","message": "'+text+'"}'
    data = data_method + data_prop
    send(data,1,'','show_notification')
    return
def open_gui(window="",mediatype="", filtervalue="",isfilter=0):
    #ausgabe('open_gui',1)
    parameter=""
    if isfilter:
        if mediatype == 'movies' or mediatype == 'tvshows':
            window = 'videos'
            filterkey = 'title'
            if mediatype == 'movies':
                destination = "videodb://movies/titles/"
            else:
                destination = "videodb://tvshows/titles/"
        else:
            window = 'music'
            if mediatype == 'artists':
                destination = "musicdb://artists/"
                filterkey = "artist"
            elif mediatype == 'genres':
                destination = "musicdb://genres/"
                filterkey = "genre"
            else:
                destination = "musicdb://albums/"
                filterkey = "album"
        parameter = ',"parameters":["'\
                    +destination+\
                    '?filter=%7b%22rules%22%3a%7b%22and%22%3a%5b%7b'\
                    '%22field%22%3a%22'\
                    +filterkey+\
                    '%22%2c%22operator%22%3a%22contains%22%2c%22value%22%3a%5b%22'\
                    +filtervalue+\
                    '%22%5d%7d%5d%7d%2c%22type%22%3a%22'\
                    +mediatype+\
                    '%22%7d"]'
    elif filtervalue != "":
        parameter = ',"parameters":["'+filtervalue+'"]'
    data_method= '"method":"GUI.ActivateWindow"'
    data_prop = ',"params":{"window": "'+window+'"'\
                +parameter+ '}'
    data = data_method + data_prop
    send(data,1,'','open_gui')
    return
def send_input(slotvalue):
    data_method= '"method":"Input.ExecuteAction"'
    data_prop = ',"params":["'+slotvalue+'"]'
    data = data_method + data_prop
    #ausgabe(send(data,1),3)
    send(data,1)
    return
def init(kodi_user,kodi_pw,kodi_ip,kodi_port,_debuglevel):
    global kodi_url
    global debuglevel
    kodi_url = 'http://'+kodi_user+':'+kodi_pw+'@'+kodi_ip+':'+kodi_port+'/jsonrpc'
    debuglevel = _debuglevel
    connected = 0
    if check_connectivity():
        print(("Kodi connected at {0}:{1}".format(kodi_ip, kodi_port)))
        connected = 1
        return connected
    else:
        print(("Kodi not found at {0}:{1}".format(kodi_ip, kodi_port)))
        return connected
