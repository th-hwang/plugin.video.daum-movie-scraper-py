# -*- coding: utf-8 -*-
import json
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import DaumScraper
from urllib import parse
import unicodedata

ADDON_SETTINGS = xbmcaddon.Addon()
ID = ADDON_SETTINGS.getAddonInfo("id")
SC = DaumScraper.CScraper()


def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log(msg="[{addon}] : {msg}".format(addon=ID, msg=msg), level=level)


def log2(msg1, msg2, level=xbmc.LOGINFO):
    xbmc.log(msg="[{addon}] {msg1}: {msg2}".format(addon=ID, msg1=msg1, msg2=msg2), level=level)


def build_lookup_string(uniqueids):
    return json.dumps(uniqueids, ensure_ascii=False)


def parse_lookup_string(uniqueids):
    return json.loads(uniqueids)


def get_params(argv):
    result = {"handle": int(argv[0])}
    if len(argv) < 2 or not argv[1]:
        return result

    query = parse.unquote(argv[1].lstrip("?"))

    # 참고 한글 자소 분리된 경우 : https://jonsyou.tistory.com/26
    # 한글의 자소가 분리된채로 입력되면 정규식 검색도 안되고 daum에 검색도 안됨.
    try:
        prepQuery = unicodedata.normalize("NFC", query)
    except:
        prepQuery = query

    log("unquoted query: '{qr}'".format(qr=prepQuery), xbmc.LOGINFO)

    result.update(parse.parse_qsl(prepQuery))
    return result


def search_for_movie(title, year, handle):
    log("Search movie with title '{title}' from year '{year}'".format(title=title, year=year), xbmc.LOGINFO)

    if year:
        title = title + "(" + year + ")"

    if uniqueids := SC.getMovieIdInfo(title):
        log("In Search for title Info:  '{msg}' ".format(msg=uniqueids), xbmc.LOGINFO)
        listitem = xbmcgui.ListItem(uniqueids["prepTitle"]["searchKeyword"], offscreen=True)
        xbmcplugin.addDirectoryItem(handle=handle, url=build_lookup_string(uniqueids), listitem=listitem, isFolder=True)
    else:
        return None


def get_details(input_uniqueids, handle):

    movieId = input_uniqueids["movieId"]
    title = input_uniqueids["prepTitle"]["searchKeyword"]

    log("GetDetail movie with daum movie id '{mId}' and title '{tl}' ".format(mId=movieId, tl=title), xbmc.LOGINFO)

    listitem = xbmcgui.ListItem(title, offscreen=True)
    movieInfo = SC.getTotalMovieInfos(movieId=movieId)
    movieInfo.update(input_uniqueids)
    listitem.setUniqueIDs({"movieId": movieId}, "daum")

    if rlt := movieInfo.get("movieInfo"):
        if rlt1 := movieInfo.get("trailerInfo", {}).get("trailerUrl"):
            rlt["trailer"] = rlt1
        listitem.setInfo("video", rlt)
        listitem.setRating("daum", rlt["rating"])

    if rlt := movieInfo.get("castInfo"):
        listitem.setCast(rlt)

    if rlt := movieInfo.get("mainPosterInfo"):
        listitem.addAvailableArtwork(rlt["image"], "poster", rlt["image"])

    if rlt := movieInfo.get("posterInfo"):
        for item in rlt:
            listitem.addAvailableArtwork(item["image"], "poster", item["image"])

    if rlt := movieInfo.get("fanartInfo"):
        listitem.setAvailableFanart(rlt)

    xbmcplugin.setResolvedUrl(handle=handle, succeeded=True, listitem=listitem)
    return True


def run():

    params = get_params(sys.argv[1:])
    enddir = True

    if "action" in params:
        action = params["action"]
        if action == "find" and "title" in params:
            search_for_movie(params["title"], params.get("year"), params["handle"])
        elif action == "getdetails" and "url" in params:
            enddir = not get_details(parse_lookup_string(params["url"]), params["handle"])
        elif action == "NfoUrl" and "nfo" in params:
            search_for_movie(params["nfo"], None, params["handle"])
        else:
            log("unhandled action: " + action, xbmc.LOGWARNING)
    else:
        log("No action in 'params' to act on", xbmc.LOGWARNING)
    if enddir:
        xbmcplugin.endOfDirectory(params["handle"])


if __name__ == "__main__":
    run()
