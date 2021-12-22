## Daum Movie Scraper in Python v1.0 for Kodi v19 Matrix


#### 1. Daum search page & APIs

* Daum Main page search : https://search.daum.net/search?w=tot&q=미나리

* Daum Movie page search : https://movie.daum.net/api/search?q=미나리&t=movie

* 미나리 movieId = "137317", productionYear=2020

* main (미나리, movieId = 137317) : http://movie.daum.net/api/movie/137317/main

* person (한예리,personId = 113780 ) : http://movie.daum.net/api/person/main/113780
  * person이 casting 되었던 작품들의 movieId, poster image, releasedate, role 과 video clip 이 있음
  * person의 인물사진은 main의 "profileImage" 를 사용해야함.

* video(미나리, movieId = 137317) : http://movie.daum.net/api/video/list/movie/137317?page=1&size=20 
  * title "메인" + "예고'' 을 찾아서 링크 가능
    * "title":"<미나리> 메인 예고편","subtitle":"메인 예고편"
    * "title":"심야식당","subtitle":" 메인예고"
    * "title":"<어벤져스: 인피니티 워> 메인 예고편","subtitle":"메인 예고편"

* photo (미나리, movieId = 137317) : http://movie.daum.net/api/movie/137317/photoList?page=1&size=12&adultFlag=T 
  * 스틸 이미지 컷 모음. 
  * 포스터, 출연진 사진은 main 에 있는 링크를 사용해야함.  

* thumbnail : https://img1.daumcdn.net/thumb/C408x596/?fname=https://t1.daumcdn.net/movie/c23137b8c082f66df707f21c9884ca38a1903efa

  * size를 정해서 원본 url로 query함. size는 정해져 있는 것으로 보임. 

  * 포스터는 큰 이미지 C408x596, 스틸이미지는 종횡비 유지를 위하여 C314x0 사용하기로함.

    | 구분        | 포스터   | 스틸     | 영상     |
    | ----------- | -------- | -------- | -------- |
    | 작은 이미지 | C146x211 | S146x83  | S146x83  |
    | 큰 이미지   | C408x596 | S408x212 | S408x212 |




#### 2. Addon Structure

* Addon 이름

  * [addon-type].[medeia-type].[your-plugin-name] 의 형태 이름을 지여야함. 
  * 대소문자를 구별하므로, 소문자로 하여야함. (Each name part is case sensitive and must be in lower case)
  * plugin.video.daum-movie-scraper-py 로함.

* 디렉토리 구조

  * root 디렉토리에 addon.py, addon.xml 파일을 두고 다른 리소스들은 resources 에 둠.
  * addon.py 
    * 메인 프로그램. 실제 실행될 python code를 작성함.
    * 이름은 마음대로 변경가능하고, 변경된 이름을 addon.xml에 정의해주어야함.
    * daum-movie-scraper.py 로함.
  * addon.xml
    * addon이 하는 일, 실행에 필요한 의존성, 실행 시작할  script 등의 kodi에게 중요한 meta data를 넘겨줌.
  * changelog.txt
    * README.md에 작성함.
  * icon.png, fanart.jpg
    * 이전 버젼에서는 root 디렉토리에 두어야 했으나, Kodi 18부터는 resource에 두고 addon.xml에서 정의함.
  * LICENSE.txt
    * GPL v3 사용

  * resources
    * root 디렉토리에 두는 파일을 제외하고 필요한 파일은 여기에  둠.
    * settings.xml
      * user-configurable setting 을 정리함.
    * icon.png
      * addon 을 나타낼때 이미지로 사용됨.
      * 256x256, 512x512 크기의 PNG 파일만 가능
      * resources/icon.png 로 하고 addon.xml 에서 \<icon> 에서 위치를 지정함 
    * fanart.jpg
      * addon을 사용할 때 배경화면으로 사용됨
      * 16:9, 1280x720, 1920x1080, 3840x2160 까지만 가능
      * 파일 크기는 1MB 이하로 해야하고, 가능한 최소화하여 사용함
    * language/
      * Kodi v19 Matrix 부터는 Strings.xml 대신에 Strings.po 문법에 맞춰 사용해야함.
      * 사용하는 id 번호가 정해져 있음.
        * strings 30000 thru 30999 reserved for plugins and plugin settings
        * strings 31000 thru 31999 reserved for skins
        * strings 32000 thru 32999 reserved for scripts
        * strings 33000 thru 33999 reserved for common strings used in add-ons
    * lib/
      * module 이나 3rd party software 를 둠
      * 만약, kodi.log 에서 addon.py를 찾을 수 없다고 하고, 에러가 나면 이 디렉토리에 \_\_init\_\_.pyo & \_\_init\_\_.py 가 없어서 일 수 있으므로, 다른 addon에서 copy함
    * data/
      * 필요한 static data 를 넣음 
      * 당 addon에는 불필요하여 삭제
    * media/
      * 필요한 static media(picture, audio, video etc.) 를 넣음 
      * 당 addon에는 불필요하여 삭제


#### 3. test_script/scraper.py 구성

* plugin 기능을 모사하는 test script

1. 파일 명을 kodi로 넘겨줌
   - 스타워즈 에피소드 6： 제다이의 귀환 (더빙) (1983) (Star Wars： Episode VI - Return of the Jedi).mp4
2. Kodi 에서 cleanTitle 을 인수로 넘겨줌
   - 제작연도와 제작연도 를 중심으로 앞 부분 title만 추출하여 "strTitleAndyear (Year).mp4" 로 리턴
   - test_script/kodi_cleanString.cpp 참조, Kodi.cleanTitleByKodi(tt)["strTitleAndYear"] 로 구현
   - 스타워즈 에피소드 6： 제다이의 귀환 (더빙) (1983).mp4
3. movieIdInfo := self.getMovieIdInfo(strKodiTitle)
   1. strKodiTitle에 movieId 가 있으면 바로 값을 리턴
      - regExpMovieId = "movieId=(\\d*)" 로 검색하여 movieId 리턴
      - 계속 잘못 찾거나 안찾아지면 Daum에서 직접 검색하여 movieId를 찾고, Kodi 재검색 대화 창에 "movieId=137137" 를 직접 입력 
   2.  prepTitle = self._getPrepTitle(strKodiTitle)
      - strCleanTitle = cleanTitle(strKodiTitle)
        -  더빙, 자막, 정식릴 등, 제목에 불필요한 부분을 삭제함. 
        -  Daum은 colon만 검색가능 : '：' (full width colon, U+FF1A ) -> ':' (colon, U+003A)로  교체
        -  스타워즈 에피소드 6: 제다이의 귀환 1983
      - 한글제목("KorTitle"), 영문제목("EngTitle"), 제작연도("year")를 갖는 딕셔너리를 리턴함.
        - prepTitle = {"KorEngTitle":"스타워즈 에피소드 6: 제다이의 귀환",
          "KorTitle":"스타워즈 에피소드 6: 제다이의 귀환", "year":"1983"} 
      - 파일명의 연도는 보통 개봉연도 이나 오류도 많음.
   3. movieIdInfo := self._getMovieId(prepTitle)
      - 파일명에 연도(prepTitle.get("year")) 가 있는 경우,  Daum Main 검색 (DAUM_SEARCH),  Daum Movie 검색(DAUM_MOVIE_SEARCH) 순으로 검색하면서 검색 결과의 제작년도나 개봉년도가 파일의 연도와 일치할 경우에만 movieId 리턴함. 
      - 파일명에 연도(prepTitle.get("year"))가 없는 경우, 일치여부 확인 안함. Daum Main 검색에서는 검색되는 결과로, Daum Movie 검색에서는 첫번째 결과를 리턴함.
      - 검색순서 1) Daum Main 검색에서 "한글+연도" 키워드로, 2) Daum Main 검색에서 "한글" 키워드로 검색, 3) Daum Movie 검색에서 "한글+연도", 4)  Daum Movie 검색에서 "한글" 키워드로 검색, 5) year 제외(prepTitle.pop("year") )하고 다시 1) ~ 4) 순 검색
      - prepTitle["searchKeyword"] 
        - 검색할 키워드를 작성함. Daum Main 검색은 연도를 쓰는 것이, Daum Movie 검색은 연도를 안쓰는 것이 검색이 잘됨
        - 한글 영화명이 있으면 한글 영화명 우선으로 "korTitle" + " " + "year" 형태로 키워드 작성함. 
          예) "스타워즈 에피소드 6: 제다이의 귀환 1983"
      - 검색 결과의 data형 확인, 동일 data형으로 변환하여 사용. 
        예) Daum Movie page API의 productionYear는 <class 'int'>, movieId = <class 'str'>
4. rlt := self.getMovieInfo(movieId=movieId)
   - DAUM_API_MAIN 에서 리턴한 string을 json 로드하여 규칙에 맞게 처리함.
   - 입력은 rltAPI = json.load(DAUM_API_MAIN의 검색결과) 또는 movieId=movieId 로 가능
   - Daum Movie 검색시에 관련된 모든 영화가 리스트되고, 리스트된  영화는 모두 parsing해야하므로, 
      유명하지 않은 영화들의 정보를 기준으로 item 들을 처리하여함.
      예) "명당" movieId=111569 검색시,  "감투봉 명당 싸움"  movieId=52625 도 리스트되므로 처리필요
   - 검색 실패해도 프로그램 중지되지 않도록  예외처리 필요함.
5. rlt := self.getCastInfo(movieId=movieId)
   - DAUM_API_MAIN 에서 리턴한 string을 json 로드하여 규칙에 맞게 처리함.
   - 입력은 rltAPI = json.load(DAUM_API_MAIN의 검색결과) 또는 movieId=movieId 로 가능
   - castInfo["role"]은 배역명 apiCast["description"]을 쓰고 없으면 주연, 출연 등의 역할 apiCast["movieJob"]\["role"] 을 사용
6. rlt := self.getMainPosterInfo(movieId=movieId)
   - DAUM_API_MAIN 에서 리턴한 string을 json 로드하여 규칙에 맞게 처리함.
   - 입력은 rltAPI = json.load(DAUM_API_MAIN의 검색결과) 또는 movieId=movieId 로 가능
   - Poster Thumbnail은 C408x596 사용
7. rlt := self.getPhotoInfo(movieId=movieId)
   - DAUM_API_PHOTO 에서 리턴한 string을 json 로드하여 규칙에 맞게 처리함.
   - 입력은 rltAPI = json.load(DAUM_API_PHOTO의 검색결과) 또는 movieId=movieId 로 가능
   - photoList?page=1&size={size}&adultFlag=T 에서 sz=1로 호출 후 sz=totalElements 로 할당 후 재호출
   - movieCategory 가 "스틸", "포스터","촬영 현장", "행사" 순으로 나옴
     - 포스터는 포스터에 저장하고, 나머지는 fanart로 저장함
   - 저장하는 최대 포스터 및 fanart 갯수는 resources/settings.xml 에서 정함.
   - 원본 url 을 주면 thumnail로 바꿔주나,  size는 정해져 있음. 아무숫자나 쓰면 페이지 못찾음.
     - 포스터는 C408x596, 스틸은 S408x212 로하려 했으나, 원본의 종횡비가 다를 경우 이미지 잘림
     - 포스터는 유지 C408x596, 스틸은 C314x0 으로 함.
8. rlt := self.getTrailerInfo(movieId=movieId)
   - DAUM_API_VIDEO 에서 리턴한 string을 json 로드하여 규칙에 맞게 처리함.
   - 입력은 rltAPI = json.load(DAUM_API_VIDEO의 검색결과) 또는 movieId=movieId 로 가능
   - 메인 예고편 링크 : title "메인" + "예고'' 을 찾아서 링크 가능
   - "videoUrl": "https://tv.kakao.com/channel/462787/cliplink/417115239"
   - "videoUrl"은 링크 페이지. 이중 예고편 소스를 추출하여 "trailerUrl"을 추가함.
   - "trailerUrl": "https://play-tv.kakao.com/embed/player/cliplink/417115239?service=und_player"
   - Kodi에서 "videoUrl" 을 쓰는지, "trailerUrl"를 쓰는지 아니면 별도의 처리가 필요한지 확인 필요



#### 4. daum-movie-scraper.py

- Kodistubs : https://romanvm.github.io/Kodistubs/index.html 

  - IDE 상에서 kodi 함수를 autocompletion이 되도록 최소한의 함수 모음.

- Kodi <--> Scraper Flow chart 

  1. [Kodi] action=find

     - Kodi에서 파일명을 검색하여 ('plugin path', 'handle', 'query', 'rsume') 

       ```python
       2021-12-05 21:22:12.382 T:64864   DEBUG <general>: StartScript - calling plugin The Movie Database Python('plugin://metadata.themoviedb.org.python/','1','?action=find&pathSettings=%7b%22RatingS%22%3a%22TMDb%22%2c%22add_tags%22%3atrue%2c%22certprefix%22%3a%22Rated%20%22%2c%22enable_fanarttv_artwork%22%3atrue%2c%22fanart%22%3atrue%2c%22fanarttv_clientkey%22%3a%22%22%2c%22fanarttv_language%22%3a%22en%22%2c%22imdbanyway%22%3afalse%2c%22keeporiginaltitle%22%3afalse%2c%22landscape%22%3atrue%2c%22language%22%3a%22en-US%22%2c%22lastUpdated%22%3a%220%22%2c%22multiple_studios%22%3afalse%2c%22originalUrl%22%3a%22%22%2c%22previewUrl%22%3a%22%22%2c%22tmdbcertcountry%22%3a%22us%22%2c%22trailer%22%3atrue%2c%22traktanyway%22%3afalse%7d&title=%eb%af%b8%eb%82%98%eb%a6%ac&year=2020','resume:false')
       ```

     - decode 하면

       ```python
       2021-12-0521:22:12.382T:64864DEBUG<general>:StartScript-callingpluginTheMovieDatabasePython('plugin://metadata.themoviedb.org.python/','1','?action=find&pathSettings={"RatingS":"TMDb","add_tags":true,"certprefix":"Rated ","enable_fanarttv_artwork":true,"fanart":true,"fanarttv_clientkey":"","fanarttv_language":"en","imdbanyway":false,"keeporiginaltitle":false,"landscape":true,"language":"en-US","lastUpdated":"0","multiple_studios":false,"originalUrl":"","previewUrl":"","tmdbcertcountry":"us","trailer":true,"traktanyway":false}&title=미나리&year=2020','resume:false')
       ```

     - query 

       - action : plugin 이 처리해야할 내용 전달,
         - find : 영화를 구별할 수 있는 uniqueids 를 확보 후 기록하여야함
         - getdetails : movie info를 확보하여 기록함.
       - pathSettings : resources/settings.xml 에 있는 id 값을 전달함.
       - title, year : 파일이름으로 title과 year를 파싱하여 전달함. year는 파일에 따라서 없을 수도 있음.

     - query 중 {title=미나리&year=2020 활용} 하여 movieId 찾고 uniqueids를 저장할 것을 지시함.

     

  2. [Plugin] uniqueids

     - 입력받은 query 로 부터 영화를 구별할 수 있는 uniqueids를 저장함. 
     - 보통 movieId 를 사용함. 예) TMDB scraper는 {"tmdb": "615643"}
     - 전달받은 query 중, title, year 을 활용하여 movieId를 찾아서 uniqueids를 저장함.
       - year는 파일에 따라서 없을 수도 있음.
       - 미나리는 uniqueids= {"daum": "137317"} 로 저장함.

     

  3. [Kodi] action=getdetails

     - ('plugin path', 'handle', 'query', 'rsume')

       ```python
       2021-12-05 21:22:15.058 T:64864   DEBUG <general>: StartScript - calling plugin The Movie Database Python('plugin://metadata.themoviedb.org.python/','1','?action=getdetails&url=%7b%22tmdb%22%3a%20%22615643%22%7d&pathSettings=%7b%22RatingS%22%3a%22TMDb%22%2c%22add_tags%22%3atrue%2c%22certprefix%22%3a%22Rated%20%22%2c%22enable_fanarttv_artwork%22%3atrue%2c%22fanart%22%3atrue%2c%22fanarttv_clientkey%22%3a%22%22%2c%22fanarttv_language%22%3a%22en%22%2c%22imdbanyway%22%3afalse%2c%22keeporiginaltitle%22%3afalse%2c%22landscape%22%3atrue%2c%22language%22%3a%22en-US%22%2c%22lastUpdated%22%3a%220%22%2c%22multiple_studios%22%3afalse%2c%22originalUrl%22%3a%22%22%2c%22previewUrl%22%3a%22%22%2c%22tmdbcertcountry%22%3a%22us%22%2c%22trailer%22%3atrue%2c%22traktanyway%22%3afalse%7d','resume:false')
       ```

     - decode하면, 

       ```python
       2021-12-0521:22:15.058T:64864DEBUG<general>:StartScript-callingpluginTheMovieDatabasePython('plugin://metadata.themoviedb.org.python/','1','?action=getdetails&url={"tmdb": "615643"}&pathSettings={"RatingS":"TMDb","add_tags":true,"certprefix":"Rated ","enable_fanarttv_artwork":true,"fanart":true,"fanarttv_clientkey":"","fanarttv_language":"en","imdbanyway":false,"keeporiginaltitle":false,"landscape":true,"language":"en-US","lastUpdated":"0","multiple_studios":false,"originalUrl":"","previewUrl":"","tmdbcertcountry":"us","trailer":true,"traktanyway":false}','resume:false')
       ```

     - query 중 url={"tmdb": "615643"} 로 활용 하여 movieInfo를 가져올 것을 지시함.

     

  4. [Plugin] movieInfos : uniqueids 를 이용하여 movie info를 scrapping 하고 저장

     - 전달받은 query 중, url={"tmdb": "615643"}을 활용하여 Daum에서 scraping 하여 movieInfo저장 

     

  5. [Kodi] action =NfoUrl : nfo 파일처리

     - ('plugin path', 'handle', 'query', 'rsume')

       ```python
       2021-12-15 00:50:52.655 T:1397176   DEBUG <general>: StartScript - calling plugin The Movie Database Python('plugin://metadata.themoviedb.org.python/','1','?action=NfoUrl&nfo=https%3a%2f%2fwww.themoviedb.org%2fmovie%2f615643-minari%3flanguage%3dko%0a&pathSettings=%7b%22RatingS%22%3a%22TMDb%22%2c%22add_tags%22%3atrue%2c%22certprefix%22%3a%22Rated%20%22%2c%22enable_fanarttv_artwork%22%3atrue%2c%22fanart%22%3atrue%2c%22fanarttv_clientkey%22%3a%22%22%2c%22fanarttv_language%22%3a%22en%22%2c%22imdbanyway%22%3afalse%2c%22keeporiginaltitle%22%3afalse%2c%22landscape%22%3atrue%2c%22language%22%3a%22en-US%22%2c%22lastUpdated%22%3a%220%22%2c%22multiple_studios%22%3afalse%2c%22originalUrl%22%3a%22%22%2c%22previewUrl%22%3a%22%22%2c%22tmdbcertcountry%22%3a%22us%22%2c%22trailer%22%3atrue%2c%22traktanyway%22%3afalse%7d','resume:false')
       ```

     - decode하면, 

       ```python
       2021-12-15 00:50:52.655 T:1397176   DEBUG <general>: StartScript - calling plugin The Movie Database Python('plugin://metadata.themoviedb.org.python/','1','?action=NfoUrl&nfo=https://www.themoviedb.org/movie/615643-minari?language=ko
       &pathSettings={"RatingS":"TMDb","add_tags":true,"certprefix":"Rated ","enable_fanarttv_artwork":true,"fanart":true,"fanarttv_clientkey":"","fanarttv_language":"en","imdbanyway":false,"keeporiginaltitle":false,"landscape":true,"language":"en-US","lastUpdated":"0","multiple_studios":false,"originalUrl":"","previewUrl":"","tmdbcertcountry":"us","trailer":true,"traktanyway":false}','resume:false')
       ```

     - nfo = "파일이름과_동일.nfo" 파일을 읽어서 내용을 리턴함. 

       - nfo 내용을 파싱해서 uniqueids 를 저장함. 이후 action=getdetails 순으로 진행됨.
       - 파일별로 별도의 디렉토리를 만들고, movie.nfo 로 써도 nfo 파일로 인식함.
       - https://movie.daum.net/moviedb/main?movieId=137317 를 nfo 파일에 넣고, movieId를 파싱함.



* TrailInfo

  * DAUM_API_VIDEO = "http://movie.daum.net/api/video/list/movie/**{movieId}**?page=1&size=20"

    * 동영상 리스트를 확보하여 subtilte에 "메인 예고, 공식 예고, 본 예고, 티저 예고, 1차, 2차 예고" 등이 있는 첫번째 traiier의 linkId를 찾음.

  * DAUM_API_TRAILER_INFO =  "https://play-tv.kakao.com/api/v1/ft/playmeta/cliplink/**{linkId}**?fileds=@html5vod&service=und_player&type=VOD" 의 "videoOutputList" 에서 가용한 예고편의 해상도가 있음. 

    * (Mode : 해상도) HIGH4 :1080p 1920x1080, HIGH : 720p1280x720, MAIN: 480p 854x480, BASE : 360p 640x360, LOW : 240p 426x240, AUDIO 0x0 로 구성되어 있음
    * 가용한 해상도를 구하고, HIGH 720p가 있을 이를 default로 사용함. 없으면 MAIN,BASE, LOW 순으로.

  * DAUM_API_TRAILER_PLAYABLE_URL = "https://play-tv.kakao.com/katz/v3/ft/cliplink/**{linkId}**/readyNplay?player=monet_html5&uuid=3244cf0161c250497bcf962be670fad0&profile=**{mode}**&service=und_player&section=und_player&fields=seekUrl,abrVideoLocationList&playerVersion=3.11.14&appVersion=96.0.4664.110&startPosition=0&tid=&dteType=PC&continuousPlay=false&autoPlay=false&contentType=&drmType=widevine&ab=&literalList=&1640124549976"

       * linkId 와 mode 를 입력으로하여 playable trailer url을 찾아냄.

       

- Debugging
  - 한글처리에서 6시간 넘게 고생함. 
  - mac용이어서 인지 모르겠는데, 한글을 자소를 분리한 형태로 다루고 보여줄 때만 모아서 보여줌.
  - Kodi 에서 보내주는 한글이 자소가 분리되어 있어서 정규식으로 검출이 안되고, daum에서도 검색이 안됨.
  - [참고] https://jonsyou.tistory.com/26
  - Kodi에서 넘겨준 파라미터를 받을 때 자소를 모아서 처리함.
    - prepQuery = unicodedata.normalize("NFC", query)




#### 5. 이전 버전에서 update 필요사항

* Blog 내 댓글에서 반영이 필요한 파일 리스트 정리 -> 반영확인 완료
* 예고편 에러 -> kakao TV 링크로 반영완료

```python
titleList = [
    # Blue 2020.02.05
    # ':' 부분을 kodi에서는 UTF8로 %ef%bc%9a 로 처리하는데 daum 은 %3a로 해야 인식
    # "한글+숫자+한글" 에서 숫자 누락
    """스타워즈 에피소드 6： 제다이의 귀환 (1983)_(Star Wars： Episode VI - Return of the Jedi)""",
    """스타워즈： 깨어난 포스 (2015)_(Star Wars： The Force Awakens)""",
    
    # 아마도 2020.04.23,  :, !를 인식하지 못함.
    """짱구는 못말려 극장판：엄청 맛있어! B급 음식 서바이벌! (2013)""",
    
    # Murian 2020.04.23, 라이브러리에서 예고편을 선택하면 스킨이 강제종료
    # 로그를 보면 이런 에러가 뜹니다.
    # 2020-04-23 13:48:45.987 T:4928 ERROR: ffmpeg[1340]: [tcp] Failed to resolve hostname
    # mmc.daumcast.net: Temporary failure in name resolution
    # Daum에서 예고편 영상을 daumcast에서 kakao TV 로 옮겼는데, 검색결과는 그대로 daumcast 로함.
    
    # 아마도 2020.04.27
    # 다음영화에서 검색하면 제작연도가 개봉연도와 표기된 연도가 달라서 불러오지 못한 것이었습니다.  
    # 제작년도와 개봉년도가 다르면 제작년도를 써야함.
    """마스크(1994)""",
    """겨울왕국(2013)""",
    """겨울왕국2(2019)""",
    """첫 키스만 50번째(2004)""",
    """심야식당(2014)""",
    
    # 책상물림 2020.05.28
    # 중간에 '-' 등의 처리
    """탐정 - 더 비기닝(2015)""",
    """탐정 - 리턴즈(2018)""",
    """엽문1""",
    """엽문2"""
]
```



#### 6. Kodi source 참조

* Kodi 파일명을 정리하여 "제목(연도)" 형태로 보냄 

```cpp
// https://github.com/xbmc/xbmc/blob/master/xbmc/settings/AdvancedSettings.cpp
// m_videoCleanDateTimeRegExp = "(.*[^ _\\,\\.\\(\\)\\[\\]\\-])[ _\\.\\(\\)\\[\\]\\-]+(19[0-9][0-9]|20[0-9][0-9])([ _\\,\\.\\(\\)\\[\\]\\-]|[^0-9]$)?";

// m_videoCleanStringRegExps.clear();
// m_videoCleanStringRegExps.emplace_back("[ _\\,\\.\\(\\)\\[\\]\\-](aka|ac3|dts|custom|dc|remastered|divx|divx5|dsr|dsrip|dutch|dvd|dvd5|dvd9|dvdrip|dvdscr|dvdscreener|screener|dvdivx|cam|fragment|fs|hdtv|hdrip|hdtvrip|internal|limited|multisubs|ntsc|ogg|ogm|pal|pdtv|proper|repack|rerip|retail|r3|r5|bd5|se|svcd|swedish|german|read.nfo|nfofix|unrated|extended|ws|telesync|ts|telecine|tc|brrip|bdrip|480p|480i|576p|576i|720p|720i|1080p|1080i|3d|hrhd|hrhdtv|hddvd|bluray|x264|h264|xvid|xvidvd|xxx|www.www|cd[1-9]|\\[.*\\])([ _\\,\\.\\(\\)\\[\\]\\-]|$)");
// m_videoCleanStringRegExps.emplace_back("(\\[.*\\])");

// for web : 
// (.*[^  _\,\.\(\)\[\]\-])[ _\.\(\)\[\]\-]+(19[0-9][0-9]|20[0-9][0-9])([ _\,\.\(\)\[\]\-]|[^0-9]$)?
// [ _\,\.\(\)\[\]\-](aka|ac3|dts|custom|dc|remastered|divx|divx5|dsr|dsrip|dutch|dvd|dvd5|dvd9|dvdrip|dvdscr|dvdscreener|screener|dvdivx|cam|fragment|fs|hdtv|hdrip|hdtvrip|internal|limited|multisubs|ntsc|ogg|ogm|pal|pdtv|proper|repack|rerip|retail|r3|r5|bd5|se|svcd|swedish|german|read.nfo|nfofix|unrated|extended|ws|telesync|ts|telecine|tc|brrip|bdrip|480p|480i|576p|576i|720p|720i|1080p|1080i|3d|hrhd|hrhdtv|hddvd|bluray|x264|h264|xvid|xvidvd|xxx|www.www|cd[1-9]|\[.*\])([ _\,\.\(\)\[\]\-]|$)
// (\[.*\])

// https://github.com/xbmc/xbmc/blob/master/xbmc/Util.cpp

void CUtil::CleanString(const std::string& strFileName,
                        std::string& strTitle,
                        std::string& strTitleAndYear,
                        std::string& strYear,
                        bool bRemoveExtension /* = false */,
                        bool bCleanChars /* = true */)
{
    
// return strTitle, strTitleAndYear, strYear
// 1) strTitleAndYear = "중경삼림.Chungking.Express.1994.Criterion.BluRay.1080p.x265.10bit.AAC-highcal.mkv"
// 2) strTitleAndYear = "가구야공주_이야기_1080p_한글자막.mkv"
// 3) strTitleAndYear = "발레리나 이야기.mp4"

  strTitleAndYear = strFileName; 

  if (strFileName == "..")
   return;

  const std::shared_ptr<CAdvancedSettings> advancedSettings = CServiceBroker::GetSettingsComponent()->GetAdvancedSettings();
  const std::vector<std::string> &regexps = advancedSettings->m_videoCleanStringRegExps;

  // https://github.com/xbmc/xbmc/blob/master/xbmc/utils/RegExp.cpp
  CRegExp reTags(true, CRegExp::autoUtf8);  // true ; case sensitive
  CRegExp reYear(false, CRegExp::autoUtf8);

// regex compile 해서 private PCRE::pcre* m_re; 에 저장
// m_videoCleanDateTimeRegExp = "(.*[^ _\\,\\.\\(\\)\\[\\]\\-])[ _\\.\\(\\)\\[\\]\\-]+(19[0-9][0-9]|20[0-9][0-9])([ _\\,\\.\\(\\)\\[\\]\\-]|[^0-9]$)?";

  if (!reYear.RegComp(advancedSettings->m_videoCleanDateTimeRegExp))
  {
    CLog::Log(LOGERROR, "{}: Invalid datetime clean RegExp:'{}'", __FUNCTION__,
              advancedSettings->m_videoCleanDateTimeRegExp);
  }
  else
  {
    
    if (reYear.RegFind(strTitleAndYear.c_str()) >= 0)
    {
      strTitleAndYear = reYear.GetMatch(1);
      strYear = reYear.GetMatch(2);
    }
  }

  // 1) strTitleAndYear = "중경삼림.Chungking.Express", strYear = "1994" 
  // 2) strTitleAndYear = "가구야공주_이야기_1080p_한글자막.mkv"
  // 3) strTitleAndYear = "발레리나 이야기.mp4"

  URIUtils::RemoveExtension(strTitleAndYear);

  // 1) strTitleAndYear = "중경삼림.Chungking.Express", strYear = "1994" 
  // 2) strTitleAndYear = "가구야공주_이야기_1080p_한글자막"
  // 3) strTitleAndYear = "발레리나 이야기"
  
// m_videoCleanStringRegExps.emplace_back("[ _\\,\\.\\(\\)\\[\\]\\-](aka|ac3|dts|custom|dc|remastered|divx|divx5|dsr|dsrip|dutch|dvd|dvd5|dvd9|dvdrip|dvdscr|dvdscreener|screener|dvdivx|cam|fragment|fs|hdtv|hdrip|hdtvrip|internal|limited|multisubs|ntsc|ogg|ogm|pal|pdtv|proper|repack|rerip|retail|r3|r5|bd5|se|svcd|swedish|german|read.nfo|nfofix|unrated|extended|ws|telesync|ts|telecine|tc|brrip|bdrip|480p|480i|576p|576i|720p|720i|1080p|1080i|3d|hrhd|hrhdtv|hddvd|bluray|x264|h264|xvid|xvidvd|xxx|www.www|cd[1-9]|\\[.*\\])([ _\\,\\.\\(\\)\\[\\]\\-]|$)");
// m_videoCleanStringRegExps.emplace_back("(\\[.*\\])");

  for (const auto &regexp : regexps)
  {
    if (!reTags.RegComp(regexp.c_str()))
    { // invalid regexp - complain in logs
      CLog::Log(LOGERROR, "{}: Invalid string clean RegExp:'{}'", __FUNCTION__, regexp);
      continue;
    }
    int j=0;
    if ((j=reTags.RegFind(strTitleAndYear.c_str())) > 0)
      strTitleAndYear = strTitleAndYear.substr(0, j); // 앞부터 찾은 위치까지 return 함. "_1080p_" 찾음.
  }

  // 1) strTitleAndYear = "중경삼림.Chungking.Express", strYear = "1994" 
  // 2) strTitleAndYear = "가구야공주_이야기"
  // 3) strTitleAndYear = "발레리나 이야기"
  
  // final cleanup - special characters used instead of spaces:
  // all '_' tokens should be replaced by spaces
  // if the file contains no spaces, all '.' tokens should be replaced by
  // spaces - one possibility of a mistake here could be something like:
  // "Dr..StrangeLove" - hopefully no one would have anything like this.

  if (bCleanChars)
  {
    bool initialDots = true;
    bool alreadyContainsSpace = (strTitleAndYear.find(' ') != std::string::npos);

    for (char &c : strTitleAndYear)
    {
      if (c != '.')
        initialDots = false;

      if ((c == '_') || ((!alreadyContainsSpace) && !initialDots && (c == '.'))) // "_" 이거나, " "가 없고, 처음이 아닌 "."이면 " "로 바꿈
      {
        c = ' ';
      }
    }
  }

  // 1) strTitleAndYear = "중경삼림 Chungking Express", strYear = "1994" 
  // 2) strTitleAndYear = "가구야공주 이야기"
  // 3) strTitleAndYear = "발레리나 이야기"

  StringUtils::Trim(strTitleAndYear);
  strTitle = strTitleAndYear;

  // 1) strTitle = "중경삼림 Chungking Express", strTitleAndYear = "중경삼림.Chungking.Express", strYear = "1994" 
  // 2) strTitle = "가구야공주 이야기", strTitleAndYear = "가구야공주 이야기"
  // 3) strTitle = "발레리나 이야기", strTitleAndYear = "발레리나 이야기"

  // append year
  if (!strYear.empty())
    strTitleAndYear = strTitle + " (" + strYear + ")";
    
  // 1) strTitle = "중경삼림 Chungking Express", strTitleAndYear = "중경삼림.Chungking.Express(1994)", strYear = "1994" 
  // 2) strTitle = "가구야공주 이야기", strTitleAndYear = "가구야공주 이야기"
  // 3) strTitle = "발레리나 이야기", strTitleAndYear = "발레리나 이야기"

  // restore extension if needed
  if (!bRemoveExtension)
    strTitleAndYear += URIUtils::GetExtension(strFileName);
}

// https://github.com/xbmc/xbmc/blob/master/xbmc/utils/URIUtils.cpp

void URIUtils::RemoveExtension(std::string& strFileName)
{
  if(IsURL(strFileName))
  {
    CURL url(strFileName);
    strFileName = url.GetFileName();
    RemoveExtension(strFileName);
    url.SetFileName(strFileName);
    strFileName = url.Get();
    return;
  }

  // strFileName = "가구야공주_이야기_1080p_한글자막.mkv"
  size_t period = strFileName.find_last_of("./\\");  // 마지막에 있는 ".", "/", "\"의 위치를 찾는다.

  if (period != std::string::npos && strFileName[period] == '.')    // 마지막에 찾은 위치의 글자가 "." 이면
  {
    //   basic_string substr(size_type pos = 0, size_type count = npos) const; 
    // pos 부터 npos 개 만큼 return, npos 가 없으면 끝까지 return
    std::string strExtension = strFileName.substr(period); // "." 부터 끝까지 return ".mkv"
    StringUtils::ToLower(strExtension); // 소문자로 ".mkv"
    strExtension += "|";    // ".mkv|"

    std::string strFileMask;
    strFileMask = CServiceBroker::GetFileExtensionProvider().GetPictureExtensions();
    strFileMask += "|" + CServiceBroker::GetFileExtensionProvider().GetMusicExtensions();
    strFileMask += "|" + CServiceBroker::GetFileExtensionProvider().GetVideoExtensions();
    strFileMask += "|" + CServiceBroker::GetFileExtensionProvider().GetSubtitleExtensions();
#if defined(TARGET_DARWIN)
    strFileMask += "|.py|.xml|.milk|.xbt|.cdg|.app|.applescript|.workflow";
#else
    strFileMask += "|.py|.xml|.milk|.xbt|.cdg";
#endif
    strFileMask += "|";

    // picture, music, video, subtitle extenstion이면 지움
    if (strFileMask.find(strExtension) != std::string::npos)
      strFileName.erase(period); // "."부터 끝까지 지움.// strFileName = "가구야공주_이야기_1080p_한글자막"
  }
}

std::string URIUtils::GetExtension(const std::string& strFileName)
{
  if (IsURL(strFileName))
  {
    CURL url(strFileName);
    return GetExtension(url.GetFileName());
  }

  size_t period = strFileName.find_last_of("./\\");
  if (period == std::string::npos || strFileName[period] != '.')
    return std::string();   // ".", "\","/"이 없거나, 마지막 찾은 것이 "." 이 아니면 빈 string return

  return strFileName.substr(period);    // "."이 있으면 "."부터끝까지 ".mkv"
}

```

