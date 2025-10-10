

1. gpt를 참고해서 youtube shorts 태그를 id와 width height를 인식하도록 만든다.

    - 발견된 패턴일

    ```python
    YOUTUBE_PATTERN = r'<(?P<type>youtube|shorts) id="(?P<id>[\w-]+)"(?:\s+(?:width="(?P<width>[\d%px]+)"|height="(?P<height>[\d%px]+)")){0,2}\s*/?>'
    ```

    

2. markdown패키지의 확장기능을 이용하기 위해 Extension을 상속한 Extension클래스를 만들고

    - extendMarkdown(self, md) 메서드를 오바라이딩하여
        - md.inlinePatterns.register()에 자체 패턴을 받아서 처리할 Patterncls( self.패턴), 이름, 우선순위)를 넣어준다.
            - 유튜브엠베드패턴 클래스는 패턴을 받아서 사용할 예정
            - **패턴클래스의 생성자에 우리가 패턴을 넘겨준다.**

    ```python
    class YouTubeEmbedExtension(Extension):
        """Markdown 확장 기능"""
        YOUTUBE_PATTERN = r'<(?P<type>youtube|shorts) id="(?P<id>[\w-]+)"(?:\s+(?:width="(?P<width>[\d%px]+)"|height="(?P<height>[\d%px]+)")){0,2}\s*/?>'
    
        def extendMarkdown(self, md):
            md.inlinePatterns.register(YouTubeEmbedPattern(self.YOUTUBE_PATTERN), "youtube_shorts", 175)
    
    ```



3. 패턴 클래스는 Pattern클래스를 상속해서 만든다.

    - 생성자에 그 패턴을 부모생성자에서 초기화되게 한다

    ```python
    class YouTubeEmbedPattern(Pattern):
        """Markdown 패턴을 찾아 <iframe> 태그로 변환"""
    
        def __init__(self, pattern):
            super().__init__(pattern)
    ```

4. 이제 Pattern클래스의 `handleMatch(self, m)`에서 m 변수에는 패턴인식된 데이터가 들어온다.

    - m.group(" `패턴식에 넣었던 <name>`")으로 잡아서 처리한다.
    - width/height 가 들어왔는지 / 들어왔다면, 전체를 잡고 / 아니면 100%를 넣어준다.
        - height의 경우 없다면, video_type이 어떤가에 따라서 가로형 youtube면 auto / shorts면 100%를 기본값으로 둔다.

    ```python
    def handleMatch(self, m):
        video_id = m.group("id")  # ID 추출 <youtube id="ID">
        video_type = m.group("type")  # "youtube" 또는 "shorts"
    
        has_width = m.group("width") or None
        width = m.group("width") if has_width else "100%"  # 기본값 100%
        has_height = m.group("height")
        # 기본값 youtube -> auto / shorts일 때는 100%
        height = m.group("height") if has_height else (
            "auto" if video_type == 'youtube' else "100%"
        )
    ```

    

5. video_url은 유튜브.com/embed/{} 다음에 youtube id를 넣어주면 shorts도 알아서 반영된다.

    - 각종 옵션을 꺼주는 것을 넣어준다.

    - 유튜브는 일부영상 공개로 올려도 내아이디는 조회가 되는 듯?

        ```
        controls=0 → 플레이어 컨트롤(재생/일시정지 버튼 등) 숨김
        
        modestbranding=1 → YouTube 로고 최소화
        
        rel=0 → 영상 종료 후 관련 동영상 숨김
        
        playsinline=1 → iOS에서 전체 화면이 아닌 인라인 재생 허용
        
        fs=0 → 전체 화면 버튼 숨김
        
        cc_load_policy=0 → 자막 기본적으로 비활성화
        
        iv_load_policy=3 → 인터랙티브 오버레이(정보 카드 등) 숨김
        
        autoplay=0 → 자동 재생 비활성화
        
        mute=0 → 음소거 비활성화
        
        showinfo=0 → (현재는 적용되지 않지만 과거에 제목/업로더 정보 숨김)
        ```

    - 그래도 다 사라지진 않고 제목/이름/구독/마크는 다 보인다.

        - fs=0 제거로 유튜브앱으로 보는 것을 넣으려했으나.. 너무 크게 나옴..

        ```python
        video_url = f"https://www.youtube.com/embed/{video_id}?controls=0&modestbranding=1&rel=0&playsinline=1&fs=0&cc_load_policy=0&iv_load_policy=3&autoplay=0&mute=0&showinfo=0"
        ```

        

6. 이제 기본값이 아니라 직접 width, height가 주어진 상황에서 -> 정규식을 이용하여 value vs unit단위를 구분한다.

    ```python
            if has_width:
                match_width = re.match(r"(\d+)(px|em|rem|%)", width)
                width_value = int(match_width.group(1)) if match_width else 100
                width_unit = match_width.group(2) if match_width else ""
    
            # height 숫자 추출 (px 또는 % 사용 가능)
            if has_height:
                match_height = re.match(r"(\d+)(px|em|rem|%)", height)
                height_value = match_height.group(1) if match_height else "auto"
                height_unit = match_height.group(2) if match_width else ""
    
    ```



7. 이제 영상이 들어갈 안쪽 iframe을 직접 만든다.

    - src는 url이 / title은 플레이어 형식으로 이름을 적고
    - video_type에 따라 
        - 가로형 youtube면, width만 지정
        - 세로형 shorts면, height가 있다면,width상관없이 height만 지정. 그다음순위 width 아니라면 기본 height 100%

    ```python
            iframe = etree.Element("iframe")
            iframe.set("src", video_url)
            iframe.set("title", "YouTube video player")
            # youtube는 width가 있으면 반영 없으면 100%
            if video_type == "youtube":
                if has_width:
                    iframe.set("width", f"{width_value}{width_unit}")
                else:
                    iframe.set("width", f"{width}")
            # shorts는 height가 있으면 우선 반영, 그다음에 weight가 있으면 반영, 없으면 100%
            else:
                if has_height:
                    iframe.set("height", f"{height_value}{height_unit}")
                elif has_width:
                    iframe.set("width", f"{width_value}{width_unit}")
                else:
                    iframe.set("height", f"{height}")
    ```

8. w/h 둘중에 1개만 반영되고 나머지는 -> aspect ratio를 기존 정해진대로 적용되게 한다.

    ```python
            # video_type에 따라 aspect-ratio 속성을 다르게 설정
            if video_type == "youtube":
                aspect_ratio = "16 / 9"
            else:
                aspect_ratio = "9 / 16"
    ```

    ```python
    iframe.set("style", f"aspect-ratio: {aspect_ratio}; max-width:100%; display: block; margin: 0 auto;")
    
    iframe.set("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture")
    iframe.set("frameborder", "0")
    iframe.set("allowfullscreen", "true")
    ```



9. 바깥을 싸는 부모는 w100 + flex + 수직수평 가운데 정렬해놓는다.

    ```python
            # 부모는 걍 100% 가운데정렬하는 flex div
            div = etree.Element("div")
            div.set("class", "youtube" if video_type == "youtube" else "shorts")
            div.set("style",
                    f"display: flex;  flex-wrap:wrap; justify-content: center; align-items: center; margin = 0.5em auto; width: 100%;")
            div.append(iframe)
    
            return div
    ```

10. md에서 아래와 같이 사용한다.

    ```html
    - youtbe든 shorts는 아무것도 안주면 width 100% 이 기본이며, short의 경우 너무 길진다.
    <shorts id="5P9bZCHE-iE"/>
    - shorts  width 50%
    <shorts id="5P9bZCHE-iE" width="50%"/>
    - shorts width 100px
    <shorts id="5P9bZCHE-iE" width="100px"/>
    ```

    

11. table내 shorts들이 width:auto로 넘치지 않게 

    - table의 row를 고정 / max-width 지정

        ```css
        table {
            border-collapse: collapse;
            border-spacing: 0;
        
            margin: 1em auto;
            width: 100%;
            max-width: 100%;
            table-layout: fixed; /* 테이블의 너비를 고정 */
            @media (max-width: 991px) {
                margin: 0.8em auto;
                width: 97%;
                max-width: 97%;
            }
        ```

        

### list-check .svg 파일을 css로색 적용

- config -> --theme-primary 변수선언은 이미 base에서 style태그안에 해놓음.

    ```html
    <style>
        :root {
            --theme-primary: {{ config['theme']['primary'] }};
            --theme-secondary: {{ config['theme']['secondary'] }};
        }
    </style>
    ```

    

```css
/* svg내부 stroke색을 아래 mask 이미지 기법으로 적용 */
background-color: var(--theme-primary); /* 색상 적용 */
-webkit-mask-image: url(./img/list_check.svg);
mask-image: url(./img/list_check.svg);
-webkit-mask-repeat: no-repeat;
mask-repeat: no-repeat;
-webkit-mask-size: contain;
mask-size: contain;
```





### 1번째 list 점 도 크기 색 변경

```css
> ul > li::before {
    content: '';
    display: block;
    position: absolute;
    left: 0;
    top: 8px;

    width: 7px;
    height: 7px;
    /*background: #4995ba;*/
    background: var(--theme-primary);
    border-radius: 50%;
}
```





### 숫자 list도 색 변경

```css
> li::before {
    position: absolute;
    left: 0;
    top: 7.5px; /* height 의 절반 */
    transform: translateY(-50%);

    content: counter(my-counter) ". ";
    display: inline-block; /* 추가 */
    width: 15px;
    height: 15px;
    /*border-radius: 50%;*/
    /*border: 1px solid var(--green);*/

    margin: 0 5px 5px 0;

    font-weight: 600;
    /*color: #4995ba;*/
    color: var(--theme-primary)
        text-align: center;
}
```



### table border-top도 변경

```css
&:has(thead) {
    /*border-top: 3px solid var(--green);*/
    border-top: 3px solid var(--theme-primary);
    background: #fff;
}
```





### 글자 진하게 등등도 수정







### 명령어

```
python setup.py install
mdr

python -m http.server --directory build
```



### jinja참고

#### jinja2에서 sort: {% set 정렬데이터 = 데이터|sort(attribute='',reverse=True) %} -> 다시 순회

![image-20250311090346996](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250311090346996.png)



#### 속성이 여러개면 `a.b`로 정렬 + for문 내부 업뎃을 위해, dict로 변수 없뎃 + if문 내부에 문서들은 endif끝내기 전에 if update문 성공시에 연도 표시(달라지면 작성)

```html
<div class="archive">
    {% set posts_sorted = posts | sort(attribute='attributes.date_parsed', reverse=True) %}
    {% set prev_year = {'value': '0000'} %}
    {% for post in posts_sorted -%}
    {% set curr_year = post['attributes']['date_parsed'].strftime('%Y') %}
    {% if curr_year != prev_year['value'] %}
    {% if prev_year.update({'value': curr_year}) %}{% endif %}
    <div class="year">
        <h3>{{ curr_year }}년</h3>
    </div>
    {% endif %}


    <div class="post">
        <div class="title">
            {{ post['attributes']['date_parsed'].strftime('%b, %m월') }}: <a href="{{ post['attributes']['path'] }}">{{
            post['attributes']['title']}}</a>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
```





### 코딩 참고

- https://strftime.org/



- regex101.com
- 