

### 이미지 inline by alt

- https://stackoverflow.com/questions/14675913/changing-image-size-in-markdown



1. **!`[]`()의 alt 글자란에 `-2inline` 이나 `-fullwidth`를 맨 끝에 적은 뒤**

    - **css로 처리한다**

    - **일단 post전용 css인 `article.css`를 만들어서 nav에는 적용안되게 하기 위해 `base.html`에 추가한다.**

    ```html
    <link rel="stylesheet" href="{{ static_path }}/style.css">
    <link rel="stylesheet" href="{{ static_path }}/article.css">
    ```

2. post의 body가 들어가는 곳에 `div.article`로 덮는다.

    ```html
    <!-- 내용 -->
    <div class="article">
    {{ post['body'] | safe }}
    </div>
    ```





#### alt속 `-xxx` 탐지 in css

1. `![]()`가 html에서는 `img[alt=]`속성으로 바뀌는데

    - **`img[alt$=]` : `alt 끝`에 배치되는 `-fullwidth` 등**
    - **`img[alt*=]` : `alt 내부에 포함`되는 `-fullwidth` 등**
    - 을 통해 탐지할 수 있다.

    

2. 일단 이미지 자체는 둥글게 꾸미고 `가운데 정렬이면서 상하간격을 1em, 모바일991에선 0.5em`을 준다

    ```css
    .article {
        /* markdown 이미지 처리 */
    
        img {
            /* 가운데 정렬 */
            display: block;
            margin: 1em auto;
            @media (max-width: 991px) {
                margin: 0.5em auto;
            }
    
            /* 꾸미기 */
            border-radius: 1em;
            border: 1px solid var(--greyf1);
        }
    ```

    

2. 이미지 1개에 대해서는 `-fullwidth` 등을 크기에 맞게 width를 준다.

    ```css
    img[alt$="-fullwidth"] {
        width: 93%;
    }
    
    img[alt$="-halfwidth"] {
        width: 50%;
    }
    
    img[alt$="-quarterwidth"] {
        width: 25%;
    }
    ```

    

3. **다중 이미지를 `-2inline` 등으로 줄 때는**

    - **img태그 자체는 `inline-block`이면서 width는 `좌우마진 2%씩 4%를 제외`시킨 `100%/n`을 사용하게 한다.**

    ```css
    img[alt$="-2inline"] {
        display: inline-block;
        /*width: 44%; !* Adjust width to fit two images inline *!*/
        /*margin: 2%; !* Adjust margin to create space between images *!*/
        width: calc(50% - 4%); /* Adjust width to fit two images inline with 2% margin on each side */
        margin: 0 2%; /* Left and right margin of 2% */
    
    }
    
    img[alt$="-3inline"] {
        /*width: 31%; !* Adjust width to fit three images inline *!*/
        /*margin: 1%; !* Adjust margin to create space between images *!*/
        width: calc(33.33% - 4%); /* Adjust width to fit three images inline with 2% margin on each side */
        margin: 0 2%; /* Left and right margin of 2% */
    }
    ```

    - **inline으로 나열될 것이기 때문에, `외부에는 p태그`가 부모로 가있을 것이다.**

        - **`부모p태그는 기본성질인 white-space:wrap`을 `nowrap으로 바꿔서, 각 img태그들이 다음줄로 안넘어가`게 한다. 혹시나 넘어가더라도 auto가 자동으로 처리되어있다?**

            ```
            1. 줄바꿈이 방지됨
            white-space: normal 또는 white-space: wrap일 때는 부모 <p> 태그 내부에서 필요한 경우 자동 줄바꿈이 발생합니다.
            하지만 white-space: nowrap을 설정하면 줄바꿈이 발생하지 않고, 자식 요소들이 한 줄에 계속 배치됩니다.
            2. 부모 요소의 크기에 따라 요소가 넘칠 수 있음
            inline-block 요소들이 한 줄로 배치되지만, 부모 요소의 너비(width)가 좁다면, 내용이 넘쳐서 부모를 벗어날 수 있음.
            이 경우 overflow: hidden, scroll, auto 같은 속성으로 넘친 내용을 처리해야 할 수도 있음.
            3. Flex와 Grid와 다른 동작
            display: flex나 display: grid를 사용할 경우 nowrap과는 별개로 레이아웃을 조정할 수 있음.
            하지만 inline-block 요소들은 기본적으로 부모 요소의 흐름을 따르기 때문에, white-space: nowrap을 적용하면 한 줄에 계속 유지됨.
            ```

    ```css
    p:has(img[alt$="-2inline"], img[alt$="-3inline"], img[alt$="-4inline"], img[alt$="-5inline"]) {
        white-space: nowrap;
        /* 가운데 정렬 for 자식img태그들 */
        text-align: center;
    
        & img {
            display: inline-block;
            border-radius: 1em;
            border: 1px solid var(--greyf1);
        }
    
        /* p의 상하마진이 이미지 3개짜리의 상하마진이 된다. */
        margin: 1em 0;
        @media (max-width: 991px) {
            margin: 0.5em 0;
        }
    }
    ```

    ![image-20250316140909124](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316140909124.png)





### alt에 -xxx를 제외하고 caption으로 달기

1. base.html에 extra_js block을 만들고, post.html에서 추가한다.

    ```html
    {% block extra_js %}
    {% endblock %}
    </body>
    </html>
    ```

    ```html
    {% block extra_js %}
    <script src="{{ static_path }}/article.js"></script>
    {% endblock %}
    ```

    ![image-20250316142420435](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316142420435.png)





2. js에서는 `-xxxx`를 삭제한 alt값을 가지고 figure > img + figcpation 태그의 구조를 만들게 한다.

    ```js
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".article img").forEach(img => {
            const altText = img.getAttribute("alt");
            if (altText) {
                const captionText = altText.replace(/ -[^ ]+$/, ''); // " -xxxx" 제거
    
                // <figure> 생성
                const figure = document.createElement("figure");
                img.parentNode.insertBefore(figure, img); // 기존 위치에 figure 삽입
                figure.appendChild(img); // img를 figure 내부로 이동
    
                // <figcaption> 생성 후 추가
                const caption = document.createElement("figcaption");
                caption.textContent = captionText;
                figure.appendChild(caption);
            }
        });
    });
    ```

    

3. css에서 img태그 역할을 figure태그가 하도록 수정 후 img태그는 figure내에서 w100을 가지게 한다

    - **img태그에 사실상 `figure:has(img[])`로 수정한 것이 대부분이다.**

    ```css
    .article {
        /* markdown 이미지 처리 */
    
        /*img {*/
    
        figure:has(img) {
            /* 가운데 정렬 */
            display: block;
            margin: 1em auto;
            @media (max-width: 991px) {
                margin: 0.5em auto;
            }
    
            /* 꾸미기 */
            border-radius: 1em;
            border: 1px solid var(--greyf1);
            overflow: hidden; /* new */
    
            /* new */
            img {
                width: 100%;
            }
        }
    
        /*img[alt$="-fullwidth"] {*/
        figure:has(img[alt$="-fullwidth"]) {
            width: 93%;
        }
    
        figure:has(img[alt$="-halfwidth"]) {
            width: 50%;
        }
    
        figure:has(img[alt$="-quarterwidth"]) {
            width: 25%;
        }
    
        /* 다중 이미지 */
    
        figure:has(img[alt$="-2inline"]) {
            display: inline-block;
            /*width: 44%; !* Adjust width to fit two images inline *!*/
            /*margin: 2%; !* Adjust margin to create space between images *!*/
            width: calc(50% - 4%); /* Adjust width to fit two images inline with 2% margin on each side */
            margin: 0 2%; /* Left and right margin of 2% */
    
        }
    
        figure:has(img[alt$="-3inline"]) {
            /*width: 31%; !* Adjust width to fit three images inline *!*/
            /*margin: 1%; !* Adjust margin to create space between images *!*/
            width: calc(33.33% - 4%); /* Adjust width to fit three images inline with 2% margin on each side */
            margin: 0 2%; /* Left and right margin of 2% */
        }
    
        p:has(img[alt$="-2inline"], img[alt$="-3inline"], img[alt$="-4inline"], img[alt$="-5inline"]) {
            white-space: nowrap;
            /* 가운데 정렬 for 자식img태그들 */
            text-align: center;
    
            /*> img {*/
    
            > figure {
                display: inline-block;
                border-radius: 1em;
                border: 1px solid var(--greyf1);
    
    
            }
    
            /* p의 상하마진이 이미지 3개짜리의 상하마진이 된다. */
            margin: 1em 0;
            @media (max-width: 991px) {
                margin: 0.5em 0;
            }
        }
    }
    ```

    ![image-20250316154444798](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316154444798.png)







### caption 디자인

1. 기본적인 글자색/배경색  +  패딩으로 상하가운데 + 가운데정렬 + 글자크기 

    ```css
    figure:has(img) {
    
        figcaption {
            padding: 1em 1.25em;
            text-align: center;
            font-size: 0.8em;
    
            color: var(--grey3c);
            background-color: var(--greyf2);
        }
    ```

    ![image-20250316160222724](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316160222724.png)



2. **img <-> caption사이 간격이 생기는 것 -> img태그가 inline으로 있을 경우 자체 여백**

    ```css
    img {
        width: 100%;
        object-fit: cover; /* 이미지가 비율을 유지하면서 꽉 차도록 설정 */
        object-position: center; /* 중앙 정렬 */
    
        display: block; /* 🔥 img<->caption 엽개 해결: inline 요소의 여백 제거 */
    }
    ```

    ![image-20250316160300322](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316160300322.png)



3. 디자인 바꾸기 및 줄임말 적용하기

    ```css
    figcaption {
        padding: 1em 1.25em;
        text-align: center;
        /*font-weight: bold;*/
    
        /*color: var(--grey3c);*/
        /*background-color: var(--greyf2);*/
        color: #fff;
        background-color: #88827b;
    
        font-size: 1.063em;
        @media (max-width: 991px) {
            font-size: 0.938em;
        }
    
        /* 긴 텍스트 줄임 (...) 적용 */
        white-space: nowrap; /* 텍스트 한 줄 유지 */
        overflow: hidden; /* 넘치는 부분 숨김 */
        text-overflow: ellipsis; /* 생략 (...) 처리 */
    }
    ```

    ![image-20250316213617350](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316213617350.png)





### -xxx의 마크가 있을 때만, figure안에 caption으로 처리 그외는 {: width= "" } 옵션으로 처리

#### -xxx => article.js => css figure를 꾸미는 상황



1. gpt에게 article.js 를 수정하게 함

    ```js
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".article img").forEach(img => {
            const altText = img.getAttribute("alt");
            // altText가 존재하고, " -" 뒤에 공백 없는 문자열이 오는 패턴 검사
            if (altText && / -[^ ]+$/.test(altText)) { // " -" 뒤에 공백 없는 문자열이 오는 패턴 검사
                const captionText = altText.replace(/ -[^ ]+$/, ''); // 마지막 " -xxxx..." 제거
    
                // <figure> 생성
                const figure = document.createElement("figure");
                img.parentNode.insertBefore(figure, img); // 기존 위치에 figure 삽입
                figure.appendChild(img); // img를 figure 내부로 이동
    
                // <figcaption> 생성 후 추가
                const caption = document.createElement("figcaption");
                caption.textContent = captionText;
                figure.appendChild(caption);
            }
        });
    });
    ```

    ![image-20250320091731166](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250320091731166.png)

2. **하지만, `{:width }`로 주는 순간, 부모가 가운데정렬 가능한 옵션이 안되어 왼쪽부터 차지한다.**

    - **js에서 width속성이 없는 경우에 한해서 width를 기본 100%로 해준다.**

    ```js
    else {
        // img태그의 부모에 가운데 정렬을 위한 부모 태그를 생성하여 그 내부에 img태그를 만들고, 자동으로 img태그들은 가운데 정렬 되도록 한다.
        // ✅ 가운데 정렬을 위한 부모 태그 생성
        const wrapper = document.createElement("div");
        wrapper.style.textAlign = "center"; // 가운데 정렬 스타일 추가
        wrapper.style.display = "block";    // 블록 요소로 변경하여 정렬 유지
        wrapper.style.margin = "0.5em auto";  // 위아래 마진 추가
        wrapper.style.width = "100%";       // 너비 100% 설정 (이미지를 감싸는 부모)
    
        // img의 기본 크기 설정
        if (!img.hasAttribute("width")) {
            img.style.width = "100%";   // 이미지 너비 100%로 설정
        }
        if (!img.hasAttribute("height")) {
            img.style.height = "auto";  // 비율 유지
    
        }
        img.style.maxWidth = "fit-content";
        img.style.borderRadius = "5px";
    
    
        // img의 부모에 wrapper 삽입
        img.parentNode.insertBefore(wrapper, img);
        wrapper.appendChild(img); // img를 wrapper 내부로 이동
    }
    ```

    ![image-20250320095542050](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250320095542050.png)







#### 😀 현재img태그의 부모 속 img태그들이 width100 이 안됬다면, 거기 추가하고 아니면 div.img-wrapper를 생성해서 추가한다.

1. gpt에게 맡김.

    - 부모를 block -> flex로 바꿔서, 남은공간 img태그들이 space-around으로 간격을 알아서 주게 한다.

        ![image-20250320103054092](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250320103054092.png)





### 😂🤣 width100기 안됬다면, lastWrapper로 img태그의 부모를 변수에 담아놓고, 추가적으로 계산되게 짜야됌

```css
else {
    // 현재 이미지의 부모에서, 위쪽에서 이미 생성된 wrapper 목록을 가져와서, 가장 마지막 wrapper를 찾는다.
    let parent = img.parentNode;
    let wrappers = parent.querySelectorAll(".img-wrapper"); // ✅ 기존 wrapper 목록 가져오기
    let lastWrapper = wrappers[wrappers.length - 1]; // ✅ 가장 마지막 wrapper 찾기

    let currentWidth = 0;

    // ✅ 마지막 wrapper속 이미지들  width 합을 currentWidth에 저장
    if (lastWrapper) {
        let existingImgs = [...lastWrapper.querySelectorAll("img")];
        currentWidth = existingImgs.reduce((sum, img) => {
            let width = img.getAttribute("width") || window.getComputedStyle(img).width;
            return sum + (parseFloat(width) || 100);
        }, 0);
    }

    // 현재 이미지 width를 계산해서후, 마지막 wrapper의 width총합(currentWidth)과 한다.
    let imgWidth = img.getAttribute("width") || window.getComputedStyle(img).width;
    imgWidth = parseFloat(imgWidth) || 100;

    let newTotalWidth = currentWidth + imgWidth;

    // console.log(`현재 이미지(${index}): ${img.getAttribute("alt")}`);
    // console.log(`현재 wrapper 총 너비: ${currentWidth}`);
    // console.log(`현재 이미지 너비: ${imgWidth}`);
    // console.log(`새로운 총 너비: ${newTotalWidth}`);

    // ✅ 마지막 wrapper가 없거나, totalWidth의 너비가 100%를 초과하면 새로운 wrapper 생성
    if (!lastWrapper || newTotalWidth > 100) {
        lastWrapper = document.createElement("div");
        lastWrapper.classList.add("img-wrapper");
        lastWrapper.style.display = "flex";
        lastWrapper.style.justifyContent = "space-around";
        lastWrapper.style.alignItems = "center";
        lastWrapper.style.flexWrap = "wrap";
        lastWrapper.style.margin = "0.5em auto";
        lastWrapper.style.width = "100%";

        parent.appendChild(lastWrapper); // ✅ 새 wrapper를 부모에 추가
        currentWidth = 0; // ✅ 새 그룹이므로 다시 계산 시작
    }

    lastWrapper.appendChild(img);
    // currentWidth += imgWidth; // ✅ 새 wrapper에서 너비 계산 시작

    // ✅ 이미지 스타일 설정
    if (!img.hasAttribute("width")) {
        img.style.width = "100%"; // 이미지 너비 100% 설정
    }
    if (!img.hasAttribute("height")) {
        img.style.height = "auto"; // 비율 유지
    }
    img.style.maxWidth = "fit-content";
    img.style.borderRadius = "1em";
    img.style.border = "1px solid #f1f3f6";

}
```

![image-20250322051146417](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322051146417.png)

![image-20250322051134720](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322051134720.png)



#### wrapper가 table속에 있다면 width를 100%가 아닌 auto 로 / img태그의 부모wrapper와 더 부모 td는 180px에  100/100/cover로 바꾸기

- isInsideTable 변수를 위로 빼서 img태그에서도 사용할 수 있게 하고

- wrapper의 parent를 while문으로 찾아가다가 tagName `TABLE`이 발견되면, treu로 표시한 것을 이용해 wrapper의 크기르 100%가 아닌 auto로 바꾸고

    ```js
    let isInsideTable = false;
    // ✅ 마지막 wrapper가 없거나, totalWidth의 너비가 100%를 초과하면 새로운 wrapper 생성
    if (!lastWrapper || newTotalWidth > 100) {
        lastWrapper = document.createElement("div");
        lastWrapper.classList.add("img-wrapper");
        lastWrapper.style.display = "flex";
        lastWrapper.style.justifyContent = "space-around";
        lastWrapper.style.alignItems = "center";
        lastWrapper.style.flexWrap = "wrap";
        lastWrapper.style.margin = "0.5em auto";
        // lastWrapper.style.width = "100%";
        // wrapper가 table속에 있다면 100% 말고, auto로
        // ✅ 테이블 내부인지 확인하고 width 조정
        let tempParent = parent;
        while (tempParent) {
            if (tempParent.tagName === "TABLE") {
                isInsideTable = true;
                break;
            }
            tempParent = tempParent.parentElement;
        }
    
        if (isInsideTable) {
            lastWrapper.style.width = "auto"; // ✅ 테이블 내부라면 auto
        } else {
            lastWrapper.style.width = "100%"; // ✅ 일반적인 경우 100%
        }
    
        parent.appendChild(lastWrapper); // ✅ 새 wrapper를 부모에 추가
    ```

- img태그의 기본 width를 정의할 때, table내부라면, img태그에서 가장 가까운 `td를 180px을 maxWidth로 넣어주고, ` padding 0 / wrapper도 magin 0 에 보더도 제거해준다.

    ```js
    if (!img.hasAttribute("width")) {
        // img.style.width = "100%"; // 이미지 너비 100% 설정
    
        // width도 없고, table 속에 있다면, 180px을 기본으로 설정
        if (isInsideTable) {
            // img.style.width = "180px";
            // ✅ 테이블 내부인지 다시 확인 (table > tr > td 구조)
            let tdParent = img.closest("td"); // 가장 가까운 <td> 찾기
            if (tdParent) {
                tdParent.style.maxWidth = "180px";
                tdParent.style.padding = "0";
    
                lastWrapper.style.margin = "0";
    
    
                img.style.width = "100%";        // <td>에 꽉 차도록 설정
                img.style.height = "100%";       // 높이도 채우도록 설정
                img.style.objectFit = "cover";   // 비율 유지하면서 <td> 가득 채우기
                img.style.maxWidth = "none";     // 최대 너비 제한 해제
    
                img.style.borderRadius = "0";
                img.style.border = "none";
    
            }
        } else {
            img.style.width = "100%"; // 이미지 너비 100% 설정
        }
    }
    ```

- test

    ![image-20250322124524277](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322124524277.png)
    ![image-20250322124533728](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250322124533728.png)







### codehighlight

1. builtin extension을 `'fenced_code', 'codehilite'`를 추가해서 적용하면 된다.

    - **여기까지 하면, `<code>태그`만 붙는데, 이것을 적용시킬 css는 아직 없다.**

    ```python
    MARKDOWN_EXTENSIONS = {
    
        'extensions': ['extra', 'toc', 'fenced_code', 'codehilite'], # extra 넣어야 테이블 가능.
    
        'extension_configs': {
            'markdown.extensions.extra': {},
            'markdown.extensions.meta': {},
        },
        'output_format': 'html5',
    }
    
    post['body'] = markdown.markdown(post['body'],
                                     **MARKDOWN_EXTENSIONS,
                                    )
    ```

    ```
    authors: [조재성]
    youtube: P_06Nvmunrk
    ---
    
    유튜브
    ​```python
    import os
    os.path.join('a', 'b')
    ​```
    ```

    ![image-20250316213913184](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316213913184.png)

    ![image-20250316214010279](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316214010279.png)



2. **`pygments`패키지 설치 후 추가로 해당 css를 추가해줘야한다.**

    ```
    pip install pygments
    ```

    ```python
    ## codehiligt css를 pygments 모듈에서 가져와서 새로쓰기 (외부 전용ㄴ)
    formatter = HtmlFormatter()
    code_highlight_css = formatter.get_style_defs()
    with open(os.path.join(OUTPUT_DIR, 'static', 'code-highlights.css'), 'w') as f:
        f.write(code_highlight_css)
    ```

    ![image-20250316214446997](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316214446997.png)

3. base.html에서 사용하도록 해준다.

    - 이미 작성된 것이므로 style.css가 더 아래 있도록 하자.

    ```html
    <link rel="stylesheet" href="{{ static_path }}/code-highlights.css">
    <link rel="stylesheet" href="{{ static_path }}/style.css">
    <link rel="stylesheet" href="{{ static_path }}/article.css">
    ```

    ![image-20250316215323273](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316215323273.png)







### table

1. css를 th와 td에 주는데

    - table은 마진을 줘놓고 w100 / 가운데 정렬 / b-top + 배경
    - th는 패딩 / 최소높이 / 배경 / 보더전체 / 수직가운데정렬
    - td는 패딩 / lh / 보더전체 / 수직가운데정렬
        - th, td는 첫번째것과 마지막것을 모바일일 때 보더 없애기

    ```css
    table {
        border-collapse: collapse;
        border-spacing: 0;
    
        margin: 1.5em auto;
        width: 100%;
        @media (max-width: 991px) {
            margin: 3em auto;
            width: 97%;
        }
    
        text-align: center;
    
        /*border: 1px solid #d5d5d5;*/
        border-top: 3px solid var(--green);
        background: #fff;
    
        & tr > th {
            padding: 15px 14px;
            @media (max-width: 991px) {
                padding: 5px 8px;
            }
            min-height: 40px;
            background: #f6f6f6;
            border-left: 1px solid #d5d5d5;
            border-right: 1px solid #d5d5d5;
            border-bottom: 1px solid #d5d5d5;
            font-weight: 700;
            vertical-align: middle;
            word-break: keep-all;
        }
    
        & tr > td {
            padding: 12px 14px;
            @media (max-width: 991px) {
                padding: 5px 8px;
            }
            line-height: 1.4;
            border-left: 1px solid #d5d5d5;
            border-right: 1px solid #d5d5d5;
            border-bottom: 1px solid #d5d5d5;
            word-break: keep-all;
            vertical-align: middle;
        }
    
        & tr > th:first-child,
            & tr > td:first-child {
                @media (max-width: 991px) {
                    border-left: none;
                }
        }
    
        & tr > th:last-child,
            & tr > td:last-child {
                @media (max-width: 991px) {
                    border-right: none;
                }
        }
    }
    ```

    

![image-20250316223248938](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250316223248938.png)





### title



### post의 title

1. post.html에서 다른 h1와 구분되게 하기 위해서 클래스를 달아준다.

    ```html
    <h1 class="post-title">{{ post['attributes']['title'] }}</h1>
    ```

2. post['body']가 아니므로 article.css가 `.article`이 아니라 외부에 

    ```css
    /* post.html */
    .post-title {
        font-size: 2em;
        font-weight: 700;
        line-height: 2em;
        color: #3c3c3c;
        margin: 0;
        word-break: keep-all;
    }
    
    
    .article {
    
        /* 소제목들 */
    
        & h3 {
    ```

    ![image-20250317124921972](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250317124921972.png)





### font 추가 후 기본 글자로

```html
<!-- font -->
<link rel="stylesheet" as="style" crossorigin
      href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"/>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@200..900&display=swap" rel="stylesheet">
```



```css
/*@import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');*/

html, body {
    font-family: Pretendard, "Noto Sans KR", "Malgun Gothic", "Apple Color Emoji",
    "Segoe UI Emoji", "Segoe UI Symbol", sans-serif;
    margin: 0;
    font-size: 100%;
    line-height: 1.65;
}
```

![image-20250317125834599](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250317125834599.png)

### h3 소제목 가운데 정렬



```css
.article {

    /* 소제목들 */
    & h3 {
        display: block;
        line-height: 1.4;
        letter-spacing: 2px;
        margin: 0 auto 1.8em;
        font-size: 2em;
        font-weight: 800;
        text-align: center;

        @media (max-width: 991px) {
            font-size: 1.5em;
        }
    }
```

![image-20250317124115197](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250317124115197.png)



### h5 before + after로 가운데구멍난원 마크 가진 제목

```css
/* 좌측 마크 h5  */

h5 {
    line-height: 1.2;
    margin: 16px 0 1em;
    padding: 0 0 0 1.414em;
    font-size: 1.125em;


    display: inline-block;
    position: relative;
    color: #3c3c3c;
    font-weight: 800;
    word-break: keep-all;

    &::before {

        position: absolute;
        content: '';
        display: inline-block;
        top: 0;
        left: 0;

        width: 18px;
        height: 18px;

        box-sizing: border-box;
        border-radius: 50%;
        /*background: linear-gradient(135deg, #4995ba 0, #495c65 18%, #ba8749 85%, #88827b 100%);*/
        background: linear-gradient(135deg, var(--main) 0, var(--green) 18%, #FC5230 85%, #FF6D62FF 100%);
    }

    &::after {
        position: absolute;
        content: '';
        display: inline-block;
        top: 5px;
        left: 5px;

        width: 8px;
        height: 8px;
        border-radius: 50%;
        box-sizing: border-box;

        background: #fff;
        box-shadow: 1px 1px 1px rgba(0, 0, 0, .2);
    }
}
```

![image-20250317140345421](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250317140345421.png)



### li - 숫자는 ol >li   VS   li - 점은 ul > li

![image-20250317141222336](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250317141222336.png)

![image-20250317141300482](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250317141300482.png)



- 

    ![image-20250317230109400](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250317230109400.png)





#### ul > li 부터

- ul은 flex로 만들어놓고 gap으로 세로 간격을 준다.
- li들은 flex-teim으로서 lh1.4에 fz1em으로 유지하며
- rel을 만들어서 before를 만들어 4px짜리 원을 만든다
- li안에 내용물이 어떤 경우는 p가 들어가기 때문에, margin 0을 p에 대해서 걸어준다.
- 꺽쇠를 써서 첫번째 ul>li에만 걸어준다. depth들어가면 복잡해지고 이상함.

```css
> ul {
    margin: 0 auto 1em;
    padding: 0;

    display: flex;
    flex-wrap: wrap;
    gap: .313em 1em;


    border: 0;
    list-style: none;
    vertical-align: baseline;


    > li {
        flex: 1 1 100%;
        margin: 0 auto;
        padding-left: 10px;

        border: 0;
        list-style: none;

        line-height: 1.4;
        font-size: 1em;


        position: relative;
        word-break: keep-all;


        &::before {
            content: '';
            display: block;
            position: absolute;
            left: 0;
            top: 8px;

            width: 4px;
            height: 4px;
            background: #4995ba;
            border-radius: 50%;
        }

        > p {
            margin: 0;

            &:last-child {
                line-height: 1.5;
                word-break: keep-all
            }
        }
    }
}
```

![image-20250318094731011](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250318094731011.png)





#### ul과 ol의 공통부분 빼고, ul 및 ol의 li에 숫자 적용하기

```css
> ul, > ol {
    margin: 0 auto 1em;
    padding: 0;

    display: flex;
    flex-wrap: wrap;
    gap: .313em 1em;


    border: 0;
    list-style: none;
    vertical-align: baseline;


    > li {
        flex: 1 1 100%;
        margin: 0 auto;
        padding-left: 10px;

        border: 0;
        list-style: none;

        line-height: 1.4;
        font-size: 1em;


        position: relative;
        word-break: keep-all;

        > p {
            margin: 0;
            display: inline-block;

            &:last-child {
                line-height: 1.5;
                word-break: keep-all
            }
        }
    }

}

> ul > li::before {
    content: '';
    display: block;
    position: absolute;
    left: 0;
    top: 8px;

    width: 4px;
    height: 4px;
    background: #4995ba;
    border-radius: 50%;
}


> ol {
    counter-reset: my-counter;
    > li {
        counter-increment: my-counter; /* 🔥 각 항목마다 카운터 증가 */
    }

    > li::before {

        content: counter(my-counter) ". ";
        display: inline-block; /* 추가 */
        width: 15px;
        height: 15px;
        /*border-radius: 50%;*/
        /*border: 1px solid var(--green);*/

        margin: 0 5px 5px 0;

        font-weight: 800;z
        color: #4995ba;
        text-align: center;
    }
}
```

![image-20250318101429028](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250318101429028.png)





### ul, ol의 2번째 li는 아이콘 넣기

1. build폴더를 보면 static에 css와 img폴더가 같이 있어서, css에서 사용할 이미지를 내부static/img에 넣고 그대로 복사되게 한다

    ![image-20250318225553944](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250318225553944.png)

    ![image-20250318225610302](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250318225610302.png)



2. css

    ```css
    /* 2단계 li 부터는 그림으로 */
    /* https://www.ansclinic.co.kr/03/01.php */
    
    > ul > li, > ol > li {
        > ul, > ol {
            list-style: none;
            margin: 0.2em auto 0;
            padding-left: 20px;
            width: 100%;
    
            > li {
                line-height: 1.4;
                margin: 0px auto 0.5em;
    
                position: relative;
                padding-left: 20px;
    
                &::before {
                    content: '';
                    display: block;
                    position: absolute;
                    left: 0;
                    top: 3px;
    
    
                    width: 15px;
                    height: 13px;
    
                    background: url(./img/list_check.png) no-repeat;
    
                    > p {
                        margin: 0 auto; /* li 자식p의 기본 마진 삭제 */
                        line-height: 1.5;
                        font-size: 1em;
    
    
                    }
                }
            }
        }
    }
    ```

    ![image-20250318225805246](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250318225805246.png)

### ul, ol의 글자 들여쓰기 by 부모rel + before abs + p-l // break-word해야 flex-item 자식들이 100% 안넘어가고 다음줄로 넘어감.





![image-20250323141615024](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323141615024.png)

```css
> ul, > ol {

    > li {
        flex: 1 1 100%;
        margin: 0 auto;

        /*padding-left: 10px;*/
        padding-left: 20px; # 
```

```css
> ol {
    counter-reset: my-counter;

    > li {
        list-style: none;
        counter-increment: my-counter; /* 🔥 각 항목마다 카운터 증가 */

        position: relative; # 
    }

    > li::before {
        position: absolute; # 
        left: 0;
        top: 7.5px; /* height 의 절반 */
        transform: translateY(-50%);

        content: counter(my-counter) ". ";
        display: inline-block; /* 추가 */
        width: 15px;
        height: 15px;
```

![image-20250323142456796](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323142456796.png)

```css
> li {
    /*word-break: keep-all;*/
    word-break: break-word;
```

![image-20250323142638106](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250323142638106.png)



### strong / italic / code / a링크

- code블락 `''`은 `'''`의 `pre > code`가 아닌 경우에만 적용되도록 한다.

    ```css
    :not(pre) > code {
        letter-spacing: 1px;
    
        font-weight: 700;
        padding: 0 0.25em;
        color: var(--submain);
        background: #fdf5e2;
    
        line-height: 1.4;
        font-size: 1em;
    
        border-radius: 4px;
    }
    ```

- 진하게는 strong이지만 이탤릭은 `strong > em`이다.

    ```css
    strong {
        letter-spacing: 1px;
    
        font-weight: 700;
        background: var(--green);
        padding: 0 0.25em;
        color: white;
    
        border-radius: 4px;
    
        /* 이탈릭 */
    
        > em {
            border-radius: 4px;
            font-style: normal;
    
            margin: 0 -0.25em; /* 부모 strong의 padding을 상쇄 */
            padding: 0 0.25em;
    
            background: #fdf5e2;
            color: var(--green);
        }
    }
    ```

- 링크는 before를 써서 기호를 앞에 달아서 처리한다.

    ```css
    /* 링크 */
    a {
    
        text-decoration: none;
    
        &:visited, &:active {
            text-decoration: none;
        }
    
        &:before {
            content: '🔗';
            display: inline-block;
            margin-right: .25em;
            border-radius: 50%;
            color: inherit;
            font-size: .875em;
        }
    
        padding: .063em .313em;
        background: #e2e9eb;
        color: #495c65;
        font-weight: 600;
    
        display: inline-block;
        border-radius: 4px;
        transition: .3s;
    }
    ```

- 인용구는 `blockquote`다

    ```css
    /* 인용구 */
    
    blockquote {
        margin: 0 auto 1em;
        padding: 1.125em;
    
        background: rgba(233, 232, 230, .5);
        border-radius: 16px;
        box-shadow: 2px 2px 12px rgba(184, 181, 177, .1);
    
    }
    ```

- **줄바꿈 `-` `-` `-`는 hr인데, 글에 3개가 붙어있으면 에러가 남.**

    ```css
    /* hr 줄바꿈 */
    hr {
        border: 0;
        border-bottom: .8rem solid var(--greyf1);
        margin: 1.5em auto;
    }
    ```

    ![image-20250319223202785](https://raw.githubusercontent.com/is2js/screenshots/main/image-20250319223202785.png)





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