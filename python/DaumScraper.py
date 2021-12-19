# -*- coding:utf-8 -*-
# Class for Daum Movie Scraper v1.0
# ver 1.0 : initial release

import requests
import re
import json


class CKodi:
    def cleanTitleByKodi(self, strFileName):

        strTitleAndYear = strFileName
        strYear = None

        if rlt := self.getCleanString(strTitleAndYear):
            strTitleAndYear = rlt

        if rlt := self.rmExtention(strTitleAndYear):
            strTitleAndYear = rlt

        if rlt := self.getTitleAndYear(strTitleAndYear):
            strTitleAndYear = rlt["strTitleAndYear"]
            strYear = rlt["strYear"]

        strTitleAndYear = re.sub("\\.|\\_", " ", strTitleAndYear)
        strTitle = strTitleAndYear

        if not strYear == None:
            strTitleAndYear = strTitleAndYear + " (" + strYear + ")"

        # return result : strTitle, strTitleAndYear, strYear
        result = {}
        result["strTitle"] = strTitle

        if rlt := self.getExtention(strFileName):
            result["strTitleAndYear"] = strTitleAndYear + rlt
        else:
            result["strTitleAndYear"] = strTitleAndYear

        if not strYear == None:
            result["strYear"] = strYear

        return result

    def getTitleAndYear(self, strFileName):
        # 프로그램에서 역슬래시 한개 제거, 이후 정규식에서 다른 한개 제거 2개 있어야
        regExp = (
            "(.*[^ _\\,\\.\\(\\)\\[\\]\\-])"
            + "[ _\\.\\(\\)\\[\\]\\-]+(19[0-9][0-9]|20[0-9][0-9])"
            + "([ _\\,\\.\\(\\)\\[\\]\\-]|[^0-9]$)?"
        )
        p = re.compile(regExp)
        rlt = p.search(strFileName)

        return {"strTitleAndYear": rlt.group(1), "strYear": rlt.group(2)} if rlt else None

    def _searchExtention(self, strFileName):
        regExg = "\\..{3}$"
        p = re.compile(regExg)
        return p.search(strFileName)

    def getExtention(self, strFileName):
        rlt = self._searchExtention(strFileName)
        return strFileName[rlt.start() :] if rlt else None

    def rmExtention(self, strFileName):
        rlt = self._searchExtention(strFileName)
        return strFileName[0 : rlt.start()] if rlt else None

    def getCleanString(self, strFileName):
        regExg = (
            "[ _\\,\\.\\(\\)\\[\\]\\-]"
            + "(aka|ac3|dts|custom|dc|remastered|divx|divx5|dsr|dsrip|dutch|dvd|dvd5|dvd9|dvdrip|dvdscr|dvdscreener|screener|dvdivx"
            + "|cam|fragment|fs|hdtv|hdrip|hdtvrip|internal|limited|multisubs|ntsc|ogg|ogm|pal|pdtv|proper|repack|rerip|retail|r3|r5"
            + "|bd5|se|svcd|swedish|german|read.nfo|nfofix|unrated|extended|ws|telesync|ts|telecine|tc|brrip|bdrip|480p|480i|576p|576i"
            + "|720p|720i|1080p|1080i|3d|hrhd|hrhdtv|hddvd|bluray|x264|h264|xvid|xvidvd|xxx|www.www|cd[1-9]|\\[.*\\])"
            + "([ _\\,\\.\\(\\)\\[\\]\\-]|$)"
        )
        p = re.compile(regExg)
        rlt = p.search(strFileName)
        return strFileName[0 : rlt.start()] if rlt else None


class CScraper:
    def _getHtml(self, url):

        hdr = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }

        return requests.get(url, headers=hdr).text

    def _getMainSearch(self, searchKeyword):
        # 참고 한글 자소 분리된 경우 : https://jonsyou.tistory.com/26
        # kwd = unicodedata.normalize("NFC", searchKeyword)
        DAUM_SEARCH = "https://search.daum.net/search?w=tot&q={kwd}"
        return self._getHtml(DAUM_SEARCH.format(kwd=searchKeyword))

    def _getMovieSearch(self, searchKeyword):

        # kwd = unicodedata.normalize("NFC", searchKeyword)
        DAUM_MOVIE_SEARCH = "https://movie.daum.net/api/search?q={kwd}&t=movie"
        html = self._getHtml(DAUM_MOVIE_SEARCH.format(kwd=searchKeyword))
        return json.loads(html)

    def _getMainAPI(self, movieId):
        DAUM_API_MAIN = "http://movie.daum.net/api/movie/{movieId}/main"
        html = self._getHtml(DAUM_API_MAIN.format(movieId=movieId))
        return json.loads(html)

    def _getPhotoAPI(self, movieId, size):
        DAUM_API_PHOTO = "http://movie.daum.net/api/movie/{movieId}/photoList?page=1&size={size}&adultFlag=T"
        html = self._getHtml(DAUM_API_PHOTO.format(movieId=movieId, size=size))
        return json.loads(html)

    def _getVideoAPI(self, movieId):
        DAUM_API_VIDEO = "http://movie.daum.net/api/video/list/movie/{movieId}?page=1&size=20"
        html = self._getHtml(DAUM_API_VIDEO.format(movieId=movieId))
        return json.loads(html)

    def _getPrepTitle(self, strKodiTitle, bAddYear=True):
        # 확장자 삭제, 한글제목, 영문제목, 제작년도가 있으면 분리해서 dictionary로 리턴
        def cleanTitle(strTitle):
            # 더빙, 정식자막, 정식릴 등 삭제
            regSub = (
                "[ _\\,\\.\\(\\)\\[\\]\\-]?"
                + "(?:더빙|정식자막|정식릴|자막|번역자막|고화질|우리말|흑백버전|합본|초고화질|4k|4K|영화|상영중)"
                + "[ _\\,\\.\\(\\)\\[\\]\\-]?"
            )

            cleanTitle = re.sub(regSub, "", strTitle)

            # ':' 부분을 kodi에서는 UTF8로 %ef%bc%9a 로 처리하는데 daum 은 %3a로 해야 인식
            cleanTitle = re.sub("：", ":", cleanTitle)
            cleanTitle = re.sub("_|-", " ", cleanTitle)

            return cleanTitle

        def getTitleAndYear(strName):
            # 프로그램에서 역슬래시 한개 제거, 이후 정규식에서 다른 한개 제거 2개 있어야
            regExp = (
                "(.*[^ _\\,\\.\\(\\)\\[\\]\\-])"
                + "[ _\\,\\.\\(\\)\\[\\]\\-]+(19[0-9][0-9]|20[0-9][0-9])"
                + "([ _\\,\\.\\(\\)\\[\\]\\-]|[^0-9]$)?"
            )

            p = re.compile(regExp)
            rlt = p.search(strName)

            return {"korEngTitle": rlt.group(1), "year": int(rlt.group(2))} if rlt else None

        def rmExtention(strName):
            regExg = "\\..{3}$"
            p = re.compile(regExg)
            rlt = p.search(strName)

            return strName[0 : rlt.start()] if rlt else strName

        def getKorTitle(strName):
            regExg = "(([0-9]+|[가-힣]).*[가-힣] ?(\\d{2}\\b|\\d\\b|\\!)?)"
            p = re.compile(regExg)
            rlt = p.search(strName)

            if rlt := p.search(strName):
                if (rlt2 := rlt.group(2)) and (rlt3 := rlt.group(3)) and (rlt2 == rlt3):
                    korTitle = strName[: rlt.start(3)].strip()
                else:
                    korTitle = rlt.group(1).strip()

            return korTitle if rlt else None

        def getEngTitle(strName):
            regExg = "([a-zA-Z].*[a-zA-Z](?: \\d{2}| \\d|\\d{2}\\b|\\d\\b|\\!)?)"
            p = re.compile(regExg)
            rlt = p.search(strName)

            return rlt.group(1) if rlt else None

        strCleanTitle = cleanTitle(strKodiTitle)  # 더빙, 정식자막, 정식릴등 삭제, 이외 특별처리

        result = dict()
        if rlt := getTitleAndYear(strCleanTitle):
            result["korEngTitle"] = rlt["korEngTitle"]
            result["year"] = rlt["year"]
        elif rlt := rmExtention(strCleanTitle):
            result["korEngTitle"] = rlt
        else:
            result["korEngTitle"] = strCleanTitle

        if rlt := getKorTitle(result["korEngTitle"]):
            result["korTitle"] = rlt
            searchKeyword = rlt

        elif rlt := getEngTitle(result["korEngTitle"]):
            result["engTitle"] = rlt
            searchKeyword = rlt
        else:
            searchKeyword = result["korEngTitle"]

        if (rlt := result.get("year")) and bAddYear:
            searchKeyword += " " + str(rlt)

        result["searchKeyword"] = searchKeyword

        return result

    def _getMovieIdByMain(self, prepTitle):
        # daum main page에서 검색하고, 제작년도와 개봉연도를 구하고, 파일의 연도와 비교하여 일치하면 movieId를 리턴함.
        # 역슬래쉬 하나는 프로그램 다른 하나는 regex 용으로 2개로 escape해야함.
        regExpMovieId = "movieId=(\\d*)"
        regExpProductionYear = "(\\d{4}) 제작"
        regExgReleasedYear = " (\\d{4}).*?개봉 "

        p = re.compile(regExpMovieId)
        q = re.compile(regExpProductionYear)
        r = re.compile(regExgReleasedYear)

        # 한글명이 있으면 한글명으로, 없으면 영문명 영문명도 없으면 파일이름으로 리턴
        # 우선 연도를 쓰고 검색후 movieId 안보이면 연도 쓰지 않고 재검색
        rltSearch = dict()
        html = self._getMainSearch(prepTitle["searchKeyword"])

        if not p.search(html):
            prepTitle = self._getPrepTitle(prepTitle["searchKeyword"], bAddYear=False)
            html = self._getMainSearch(prepTitle["searchKeyword"])

        if rlt := p.search(html):
            rltSearch["movieId"] = rlt.group(1)
        if rlt := q.search(html):
            rltSearch["prodcutionYear"] = int(rlt.group(1))
        if rlt := r.search(html):
            rltSearch["releasedYear"] = int(rlt.group(1))

        if year := prepTitle.get("year"):
            if self._isCorrectYear(year, rltSearch):
                return rltSearch.get("movieId")
            else:
                return None
        else:
            return rltSearch.get("movieId")  # movieId가 있으면 리턴, 없으면 None

    def _getMovieIdByMovie(self, prepTitle):
        # daum movie page에서 검색하고, 리스트 중에서 제작년도와 개봉연도가 일치하면 movieId를 리턴함.
        # 여러개 검색되면 첫번째 일치하는 항목의 movieId가 리턴. 제작년도가 없으면 첫번째의 movieId 리턴
        # 영화 이외에 시상 등의 기타 정보를 모두 포함 : DAUM_MOVIE_SEARCH = "https://movie.daum.net/api/search/all?q={kwd}"
        # 영화 정보만 포함 : DAUM_MOVIE_SEARCH = "https://movie.daum.net/api/search?q={kwd}&t=movie"

        rltApi = self._getMovieSearch(prepTitle["searchKeyword"])
        if not rltApi["result"]["search_result"]["meta"]["total_count"]:
            prepTitle = self._getPrepTitle(prepTitle["searchKeyword"], bAddYear=False)
            rltApi = self._getMovieSearch(prepTitle["searchKeyword"])

        if rltApi["result"]["search_result"]["meta"]["total_count"]:
            rltSearch = dict()
            if year := prepTitle.get("year"):
                for item in rltApi["result"]["search_result"]["documents"]:
                    rltSearch["movieId"] = item["document"]["movieId"]
                    if rYear := self.getMovieInfo(movieId=rltSearch["movieId"]).get("premiered"):
                        rltSearch["releasedYear"] = int(rYear[0:4])
                    rltSearch["prodcutionYear"] = item["document"]["productionYear"]

                    if self._isCorrectYear(year, rltSearch):
                        return rltSearch.get("movieId")
            else:
                return rltApi["result"]["search_result"]["documents"][0]["document"].get("movieId")
            return None
        else:
            return None

    def _isCorrectYear(self, year, rltSearch):
        return year == rltSearch.get("prodcutionYear") or year == rltSearch.get("releasedYear")

    def _getMovieId(self, prepTitle):

        if movieId := self._getMovieIdByMain(prepTitle):
            return {"movieId": movieId, "prepTitle": prepTitle}
        elif movieId := self._getMovieIdByMovie(prepTitle):
            return {"movieId": movieId, "prepTitle": prepTitle}
        else:
            return None

    def getMovieIdInfo(self, strKodiTitle):

        # 안찾아지면 movieId=137317 과 같이 직접 씀
        regExpMovieId = "movieId=(\\d*)"
        p = re.compile(regExpMovieId)
        if (rlt := p.search(strKodiTitle)) is None:
            prepTitle = self._getPrepTitle(strKodiTitle)
            if movieIdInfo := self._getMovieId(prepTitle):
                return movieIdInfo
            elif prepTitle.get("year"):
                # year 제외하고 다시 시작
                prepTitle2 = self._getPrepTitle(prepTitle.get("korEngTitle"))
                return self._getMovieId(prepTitle2)
            else:
                return None
        else:
            movieId = rlt.group(1)
            prepTitle = {"korEngTitle": strKodiTitle, "searchKeyword": strKodiTitle}

        return {"movieId": movieId, "prepTitle": prepTitle}

    def getMovieInfo(self, **kwargs):  # rltAPI= mainAPI, movieId=137317

        movieInfo = dict()
        rltAPI = kwargs.get("rltAPI")

        if movieId := kwargs.get("movieId"):
            rltAPI = self._getMainAPI(movieId)

        #  json 에서 null 은 None으로 처리
        if rltAPI and (apiMovieCommon := rltAPI.get("movieCommon")):
            if rlt := apiMovieCommon.get("titleKorean"):
                movieInfo["title"] = rlt
            if rlt := apiMovieCommon.get("titleEnglish"):
                movieInfo["originaltitle"] = rlt
            if rlt := apiMovieCommon.get("productionYear"):
                movieInfo["year"] = int(rlt)
            if rlt := apiMovieCommon.get("genres"):
                movieInfo["genre"] = [item for item in rlt]
            if rlt := apiMovieCommon.get("avgRating"):
                movieInfo["rating"] = float(rlt)
            if rlt := apiMovieCommon.get("plot"):
                movieInfo["plot"] = rlt.replace("<br>", "\n").replace("<b>", "").replace("</b>", "").strip()
            if rlt := apiMovieCommon.get("productionCountries"):
                movieInfo["country"] = [item for item in rlt]

            if rlt := apiMovieCommon.get("countryMovieInformation"):
                apiMovieCommonCountry = rlt[0]
                for item in rlt:
                    if item["country"]["id"] == "KR":
                        apiMovieCommonCountry = item
                        break

                if rlt := apiMovieCommonCountry.get("admissionCode"):
                    movieInfo["mpaa"] = rlt
                if rlt := apiMovieCommonCountry.get("releaseDate"):
                    movieInfo["premiered"] = rlt
                if rlt := apiMovieCommonCountry.get("duration"):
                    movieInfo["duration"] = int(rlt) * 60

        return {"movieInfo": movieInfo} if len(movieInfo) > 0 else None

    def getCastInfo(self, **kwargs):  # rltAPI= mainAPI, movieId=137317
        castInfo = list()
        rltAPI = kwargs.get("rltAPI")

        if movieId := kwargs.get("movieId"):
            rltAPI = self._getMainAPI(movieId)

        order = 1
        if rltAPI and (apiCasts := rltAPI.get("casts")):
            for apiCast in apiCasts:
                item = dict()
                item["role"] = apiCast["description"] if apiCast["description"] else apiCast["movieJob"]["role"]
                item["name"] = apiCast["nameKorean"] if not apiCast["nameKorean"] == "" else apiCast["nameEnglish"]
                if apiCast["profileImage"]:
                    item["thumbnail"] = apiCast["profileImage"]
                item["order"] = order

                order += 1
                castInfo.append(item)

        return {"castInfo": castInfo} if len(castInfo) > 0 else None

    def getMainPosterInfo(self, **kwargs):  # rltAPI= mainAPI, movieId=137317

        rltAPI = kwargs.get("rltAPI")
        if movieId := kwargs.get("movieId"):
            rltAPI = self._getMainAPI(movieId)

        imageUrl = None
        if rltAPI and (apiMovieCommon := rltAPI.get("movieCommon")):
            if apiMainPhoto := apiMovieCommon.get("mainPhoto"):
                imageUrl = apiMainPhoto.get("imageUrl")

        return {"mainPosterInfo": {"image": imageUrl, "preview": self._getThumbnail(imageUrl)}} if imageUrl else None

    def _getThumbnail(self, imageUrl, mode="poster"):
        size = "C408x596" if mode == "poster" else "C314x0"
        return "https://img1.daumcdn.net/thumb/{size}/?fname={url}".format(size=size, url=imageUrl)

    def getPhotoInfo(self, **kwargs):  # rltAPI= photoAPI, movieId=137317
        rltAPI = kwargs.get("rltAPI")
        if movieId := kwargs.get("movieId"):
            rltAPI = self._getPhotoAPI(movieId, 1)

        result = dict()
        if rltAPI and (apiPhoto := rltAPI.get("page")):
            if size := apiPhoto.get("totalElements"):
                rltAPI = self._getPhotoAPI(movieId, size)

            if apiPhotoContents := rltAPI.get("contents"):

                max_poster = kwargs.get("max_poster") if kwargs.get("max_poster") else 10
                max_fanart = kwargs.get("max_fanart") if kwargs.get("max_fanart") else 10
                idx_poster = 0
                idx_fanart = 0
                posterInfo = list()
                fanartInfo = list()

                for item in apiPhotoContents:
                    if item.get("movieCategory") == "포스터" and idx_poster < max_poster:
                        if imageUrl := item.get("imageUrl"):
                            posterInfo.append({"image": imageUrl, "preview": self._getThumbnail(imageUrl, "poster")})
                            idx_poster += 1
                    elif idx_fanart < max_fanart:
                        if imageUrl := item.get("imageUrl"):
                            fanartInfo.append({"image": imageUrl, "preview": self._getThumbnail(imageUrl, "still")})
                            idx_fanart += 1

                if len(posterInfo) > 0:
                    result.update({"posterInfo": posterInfo})
                if len(fanartInfo) > 0:
                    result.update({"fanartInfo": fanartInfo})

        return result if len(result) > 0 else None

    def getTrailerInfo(self, **kwargs):  # rltAPI= videoAPI, movieId=137317
        rltAPI = kwargs.get("rltAPI")
        if movieId := kwargs.get("movieId"):
            rltAPI = self._getVideoAPI(movieId)

        if rltAPI and (apiVideoContents := rltAPI.get("contents")):
            p = re.compile("메인|공식")
            q = re.compile("예고")
            r = re.compile("(\\d*)$")

            # "videoUrl": "https://tv.kakao.com/channel/462787/cliplink/417115239" 이 페이주 중에서 아래가 player
            # https://play-tv.kakao.com/embed/player/cliplink/417115239?service=und_player

            DAUM_API_TRAILER = "https://play-tv.kakao.com/embed/player/cliplink/{id}?service=und_player"

            for item in apiVideoContents:

                if title := item.get("title"):
                    if p.search(title) and q.search(title):
                        if videoUrl := item.get("videoUrl"):
                            if id := r.search(videoUrl).group(1):
                                item["trailerUrl"] = DAUM_API_TRAILER.format(id=id)
                                return {"trailerInfo": item}

        return None

    def getTotalMovieInfos(self, **kwargs):  # strKodiTitle = strKodiTitle, movieIdInfo = movieIdInfo, movieId=137317
        def _getTotalMovieInfosByMovieId(movieId):
            movieInfos = {"movieId": movieId}
            if rlt := self.getMovieInfo(movieId=movieId):
                movieInfos.update(rlt)

            if rlt := self.getCastInfo(movieId=movieId):
                movieInfos.update(rlt)

            if rlt := self.getMainPosterInfo(movieId=movieId):
                movieInfos.update(rlt)

            if rlt := self.getPhotoInfo(movieId=movieId):
                movieInfos.update(rlt)

            if rlt := self.getTrailerInfo(movieId=movieId):
                movieInfos.update(rlt)

            return movieInfos

        def _getTotalMovieInfosByMovieIdInfo(movieIdInfo):
            if movieId := movieIdInfo.get("movieId"):
                return _getTotalMovieInfosByMovieId(movieId)
            return None

        movieInfos = dict()

        if strKodiTitle := kwargs.get("strKodiTitle"):
            if movieIdInfo := self.getMovieIdInfo(strKodiTitle):
                movieInfos.update(movieIdInfo)
                if rlt := _getTotalMovieInfosByMovieIdInfo(movieIdInfo):
                    movieInfos.update(rlt)
        elif movieIdInfo := kwargs.get("movieIdInfo"):
            movieInfos.update(movieIdInfo)
            if rlt := _getTotalMovieInfosByMovieIdInfo(movieIdInfo):
                movieInfos.update(rlt)
        elif movieId := kwargs.get("movieId"):
            movieInfos["movieId"] = movieId
            if rlt := _getTotalMovieInfosByMovieId(movieId):
                movieInfos.update(rlt)

        return movieInfos if len(movieInfos) > 0 else None


class CTest(CKodi, CScraper):
    def componentTest(self):
        print("\n[Movie Info] -------------")
        print(self.getMovieInfo(movieId=0))  # None
        print(self.getMovieInfo(rltAPI={}))  # None
        print(self.getMovieInfo(movieId=52625))  # dict()
        print(self.getMovieInfo(movieId=137317))  # dict()

        print("\n[Cast Info] -------------")
        print(self.getCastInfo(movieId=0))  # None
        print(self.getCastInfo(rltAPI={}))  # None
        print(self.getCastInfo(movieId=52625))  # dict()
        print(self.getCastInfo(movieId=137317))  # dict()

        print("\n[Main Poster Info] -------------")
        print(self.getMainPosterInfo(movieId=0))  # None
        print(self.getMainPosterInfo(rltAPI={}))  # None
        print(self.getMainPosterInfo(movieId=52625))  # dict()
        print(self.getMainPosterInfo(movieId=137317))  # dict()

        print("\n[Photo Info] -------------")
        print(self.getPhotoInfo(movieId=0))  # None
        print(self.getPhotoInfo(rltAPI={}))  # None
        print(self.getPhotoInfo(movieId=52625))  # None
        print(self.getPhotoInfo(movieId=137317))  # dict()

        print("\n[Trailer Info] -------------")
        print(self.getTrailerInfo(movieId=0))  # None
        print(self.getTrailerInfo(rltAPI={}))  # None
        print(self.getTrailerInfo(movieId=52625))  # None
        print(self.getTrailerInfo(movieId=137317))  # dict()

    def mkDaumAPIJson(self, strKodiTitle):

        if movieInfo := self.getTotalMovieInfos(strKodiTitle=strKodiTitle):
            if rlt := movieInfo.get("movieInfo"):
                title = rlt.get("title")
            else:
                title = "noTitle"

            if movieId := movieInfo.get("movieId"):
                APIs = {
                    "DAUM_API_MAIN": "http://movie.daum.net/api/movie/{movieId}/main",
                    "DAUM_API_PHOTO": "http://movie.daum.net/api/movie/{movieId}/photoList?page=1&size=20&adultFlag=T",
                    "DAUM_API_VIDEO": "http://movie.daum.net/api/video/list/movie/{movieId}?page=1&size=20",
                }

                for apiName, apiUrl in APIs.items():
                    html = self._getHtml(apiUrl.format(movieId=movieId))
                    rltAPI = json.loads(html)
                    with open(
                        "test_script/Raw_{an}_{tl}_{mId}.json".format(an=apiName, tl=title, mId=movieId), "w"
                    ) as f:
                        json.dump(rltAPI, f, indent=4, ensure_ascii=False)

                with open("test_script/Movie_Info_{tl}_{mId}.json".format(tl=title, mId=movieId), "w") as f:
                    json.dump(movieInfo, f, indent=4, ensure_ascii=False)

        return None

    def fieldTest(self, page=1, flagWrite=False):

        titleList = list()
        failedTitleList = list()
        URL = "https://www.torrentreel54.top/list.php?b_id=tmovie&page={pg}"
        p = re.compile('title"\>(.*?)\<\/a\>')

        for pg in range(1, page + 1):
            html = self._getHtml(URL.format(pg=pg))
            if not (tl := p.findall(html)) == None:
                titleList.extend(tl)

        with open("test_script/Test_Title_List.json", "w") as f:
            json.dump(titleList, f, indent=4, ensure_ascii=False)

        for ff in titleList:
            print(ff, end="")
            if movieIdInfo := self.getTotalMovieInfos(strKodiTitle=ff):
                if rlt := movieIdInfo.get("movieId"):
                    print("(" + rlt + ")")
                else:
                    print("(None)")
                    failedTitleList.append(ff)
            else:
                print("(None)")
                failedTitleList.append(ff)

        if flagWrite == True:
            with open("test_script/Failed_Title_List.json", "w") as f:
                json.dump(failedTitleList, f, indent=4, ensure_ascii=False)

        return True

    def mkTestImageHtml(self, inList):

        if type(inList) is str:
            with open(inList, "r") as f:
                titleList = json.load(f)
        else:
            titleList = inList

        tot = 0
        hit = 0
        fHtml = open("test_script/test_image.html", "w")
        fHtml.write("<!DOCTYPE html>\n<html>\n<head>\n<title>Test Page</title>\n</head>\n<body>\n")

        for tt in titleList if type(titleList) is list else [titleList]:
            tot += 1
            keyword = title = year = preview = None

            strKodiTitle = self.cleanTitleByKodi(tt)["strTitleAndYear"]  # Kodi's reutrn value

            if movieInfo := self.getTotalMovieInfos(strKodiTitle=strKodiTitle):
                if movieId := movieInfo.get("movieId"):
                    hit += 1
                    if rlt := movieInfo.get("prepTitle"):
                        keyword = rlt.get("searchKeyword")
                    if rlt := movieInfo.get("movieInfo"):
                        title = rlt.get("title")
                        year = rlt.get("year")
                    if rlt := movieInfo.get("mainPosterInfo"):
                        preview = rlt.get("preview")

                    fHtml.write(
                        "<p> {tot}. {tl} (KWD : {kwd})<br>\n".format(tot=str(tot), tl=strKodiTitle, kwd=keyword)
                    )
                    fHtml.write(
                        "Result : {title} ({year} 제작) (movieID : {mId})<br>\n".format(
                            title=title,
                            year=str(year),
                            mId=movieId,
                        )
                    )
                    fHtml.write('<img src="{src}"</p><br>\n'.format(src=preview))
                else:
                    fHtml.write("Result : None</b></p>\n")

                print(str(tot) + ". " + strKodiTitle + " (" + str(keyword) + ") : ", end="")
                print(movieId)

        print("----------------------------------")
        print("hit/total = {hit}/{tot}".format(hit=hit, tot=tot))

        fHtml.write("</body>\n</html>")
        fHtml.close()

    def testTitleListInBlog(self):
        titleList = [
            # Blue 2020.02.05
            # Daum은 colon으로 작성, full width colon은 인식못함
            # "한글+숫자+한글" 에서 숫자 누락
            "스타워즈 에피소드 6： 제다이의 귀환 (1983)_(Star Wars： Episode VI - Return of the Jedi).mkv",
            "스타워즈： 깨어난 포스 (2015)_(Star Wars： The Force Awakens).mkv",
            # 아마도 2020.04.23,  :, !를 인식하지 못함.
            "짱구는 못말려 극장판：엄청 맛있어! B급 음식 서바이벌!(2013).mkv",
            # Murian 2020.04.23, 라이브러리에서 예고편을 선택하면 스킨이 강제종료
            # 로그를 보면 이런 에러가 뜹니다.2020-04-23 13:48:45.987 T:4928 ERROR: ffmpeg[1340]:
            # [tcp] Failed to resolve hostname mmc.daumcast.net: Temporary failure in name resolution
            # Daum에서 예고편 영상을 daumcast에서 kakao TV 로 옮겼는데, 검색결과는 그대로 daumcast 로함.
            # 아마도 2020.04.27
            # 다음영화에서 검색하면 제작연도가 개봉연도와 표기된 연도가 달라서 불러오지 못한 것이었습니다.  제작년도와 개봉년도가 다르면 제작년도를 써야함.
            "마스크(1994).mkv",
            "겨울왕국(2013).mkv",
            "겨울왕국2(2019).mkv",
            "첫 키스만 50번째(2004).mp4",
            "심야식당(2014).mp4",
            # 책상물림 2020.05.28
            # 중간에 '-' 등의 처리
            "탐정 - 더 비기닝(2015)",
            "탐정 - 리턴즈(2018)",
            "엽문1",
            "엽문2",
            "중경삼림.Chungking.Express.1994.Criterion.BluRay.1080p.x265.10bit.AAC-highcal.mkv",
            "천장지구.A.Moment.of.Romance.1990.BRRip.1080p.x265.10bit.AAC-highcal.mkv",
            "movieId=137317",
            "Space.Sweepers.2021.1080p.NF.WEBRip.AAC5.1.x264-Rapta.mkv",
            "알라딘.Aladdin.2019.1080p.KOR.FHDRip.H264.AAC-RTM.mkv",
        ]
        self.mkTestImageHtml(titleList)

    def testTotalMovieInfos(self, strKodiTitle):
        print("[ strKodiTitle ] ----------------------- ")
        print(json.dumps(self.getTotalMovieInfos(strKodiTitle=strKodiTitle), indent=4, ensure_ascii=False))

        print("[ movieIdInfo ] ------------------------ ")
        movieIdInfo = self.getMovieIdInfo(strKodiTitle)
        print(json.dumps(self.getTotalMovieInfos(movieIdInfo=movieIdInfo), indent=4, ensure_ascii=False))

        print("[ movieId ] ---------------------------- ")
        print(json.dumps(self.getTotalMovieInfos(movieId=movieIdInfo.get("movieId")), indent=4, ensure_ascii=False))

    def testRun(self):

        # self.componentTest()
        # self.mkDaumAPIJson("미나리 2020.mp4")
        # self.fieldTest(page=1, flagWrite=True)
        # self.mkTestImageHtml("test_script/Test_Title_List.json")
        # self.testTitleListInBlog()
        # self.testTotalMovieInfos("미나리 2020.mp4")
        self.testTotalMovieInfos("천공의-성_라퓨타.mp4")


if __name__ == "__main__":

    CTest().testRun()
