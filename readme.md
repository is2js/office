- 참고 유튜브
    - [PageKey](https://www.youtube.com/watch?v=xfIKCp-k1VQ)
    - [깃허브](https://github.com/stephengrice/markdown-sitegen)
- mdr 업데이트 후 빌드 후 루트의 index.html을 서버 띄우기
    ```shell
    python setup.py install && mdr && python -m http.server [7777] --directory build
    ```
- 특정폴더의 index.html을 서버로 띄우기
    ```shell
    python -m http.server [8000] --directory [alpinejs/xxxx]
    ```

- 만약, 포트가 사용중이라면?
    - 걸리는 모든 pid들을 반복해서 제거 
    - windows
        ```shell
        netstat -ano | findstr [8000]
        taskkill /PID <PID> /F
        ```
    - mac
        ```shell
        lsof -i :8000
        kill -9 <PID>
        ```


### 셋업 관련
1. `.gitignore`
    ```
    __pycache__
    build/
    dist/
    *.egg-info
    ```
    - `build/`폴더는 로컬 terminal에서 빌드된 결과물이며, 로컬서버를 띄울 때 경로에 들어가지만, github action을 통해 github에서 직접 빌드 후 새로운 build폴더가 사용될 것임.
    -  `dist/`폴더는 로컬 terminal에서 우리가 정의한 mdr패키지를 사용하기 위한 파일이 저장되며, 역시 github action을 통해 github에서 직접 빌드 후 새로운 dist폴더가 사용될 것임.

### github actions
- [한글참고](https://www.youtube.com/watch?v=c6yb4kbrN0E&list=PLOemN3LiCpznJPO_j5f4_WnUYRabk3mOr)
- [원본 유튜브-내용은 없고 초반에 파일소개만](https://www.youtube.com/watch?v=xfIKCp-k1VQ)
1. 루트부터 `.github/workflows/` 경로에 `gh-pages.yml` 파일 생성
    ```yml
    name: Github Pages
    on:
      push:
        branches:
          - master  # Set a branch name to trigger deployment
        #pull_request:
    
    jobs:
      deploy:
        runs-on: ubuntu-latest # 시작OS
        permissions: # 권한 설정
          contents: write
        concurrency: # 동시성 설정
          group: ${{ github.workflow }}-${{ github.ref }} # 동시성 그룹 설정
        steps:
          - run: echo "🎉 The job was automatically triggered by a ${{ github.event_name }} event."
          - run: echo "🎉 The job is now running on a ${{ runner.os }} server hosted by Github!"
          - run: echo "🔎 The name  of your branch is  ${{ github.ref }} and your repository is ${{ github.repository }}."
    
          - name: Checkout Repository # 체크아웃 = 클론?
            uses: actions/checkout@v3
          - run: echo "?? The ${{  github.repository }} repository has been cloned out to ${{ github.workspace }} on the runner."
    
          - name: List files # 파일 목록 출력
            run: |
              ls ${{ github.workspace }}
    
          - run: echo "🍏 This job's status is ${{ job.status }}." 
    ```
   

2. github repository 공유
    1. 설정 > github검색 > 로그인 -> 안되서 삭제후 -> token으로 로그인 -> 링크를 통해 깃허브 로그인하여 <쓰기권한까지 넣어> 토큰생성후 입력 -> 그래도 안되면 pycharm 업데이트
        - 토큰은 깃허브 개발자 설정에서 person 쪽에서 생성하고 있음.
        - 안되면 
   2. 상단 git > github > 프로젝트 공유
3. local git 설정
    - push해도 올라가지 않는다.
    ```
    git@github.com: Permission denied (publickey).
    fatal: Could not read from remote repository.
    Please make sure you have the correct access rights
    and the repository exists.
    ```
    - local에서 public key생성 by ssh키 생성 
        - 비번은 입력안하고 enter로 넘겨도 됨. 
        ```shell
        ssh-keygen -t rsa -C “본인 GitHub 계정 이메일”
        cat ~/.ssh/id_rsa.pub # 생성한 키 확인 (github에 등록할 키)
        ```
    - github > settings > ssh and gpg keys > new ssh key에 추가


4. git > github > 프로젝트 공유 후, 해당 repository로 이동하여 actions탭에서 방금 만든 yml파일이 잘 작동하는지 확인

5. yml에 `build` 후  `gh-pages`브랜치에 푸시하는 코드 추가
    ```yml
      - name: Build site # 로컬 터미널에서 하던 python 패키지 빌드 작업
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt # mdr 패키지는 주석처리?
          
          
          pip install -e . # 로컬의 python setup.py install 대신
          mdr
      - name: Deploy Github Pages # gh-pages에 빌드한 것과 함께 배포 (빌드한 내용물을 pull request로 gh-pages 브랜치에 반영)
        uses: peaceiris/actions-gh-pages@v3
        if: ${{ github.ref == 'refs/heads/master' }}
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./build
    ```
   

6. settings > pages에서
    - deploy form a branch를 통해 배포가 `~.github.io/레포명`으로 되는 것을 확인한다.
       - . `gh-pages`브랜치와 `/root`폴더로 설정
    - 이렇게 branch를 통한 정적인 배포는 단점이 커스텀 도메인이 없는 경우 `~.github.io/레포명`으로서 `레포명이 path로 붙어벼려 index.html에 걸어둔 상대경로가 꼬이게 된다.`
    - 또한, master 커밋시 gh-pages로 build폴더의 내용물이 가긴하지만,  deployment 트리거가 제대로 작동안되는 경우가 많아서 
    - v4로 바꿈
    ```yml
          - name: Deploy
            uses: peaceiris/actions-gh-pages@v4
            with:
              github_token: ${{ secrets.GITHUB_TOKEN }} # 자동생성 되어 있는 토큰
              publish_dir: ./build
    ```

7. 문제는 is2js.github.io/<레포명>으로서 path기본에 <레포명>까지가 기본이 되어버린다.
    - 로컬에서 명령어로 --directory build로  build의 index.html이 path없이 localhost:7777에 떴지만
    - github pages에서는 is2js.github.io/<레포명>으로서 path에 레포명이 붙어버려 gh-pages 루트 index.html이 github.io/office/에서 index.html이 되는데
    - 문제는, 상대 경로들이 전부 ../static/ 형태로 들어가져있으므로, 클릭하면 path에 해당하는 /office가 사라져서 에러가 난다.
    - 그러므로 개별 repo github pages를 만들 땐, localhost:포트번호로 띄울게 아니라 repo명까지 고려해서 클릭이 되게 한다.
    - 일단 index.html의 상대경로를 ../에서 ./로 강제한다.
    ```python
    def render_html(page, config, env, posts, title='Home', root_path_back_level=0, **others):
        html_template = env.get_template(page)
    
        if __name__ == '__main__':
            # is_test=True -> 내부에서 ../ 갯수 줄이는 것 안함.
            relative_root_path = get_relative_root_path(page, is_test=True)
            static_path = os.path.join(relative_root_path, 'md_templates', 'static')
        else:
            relative_root_path = get_relative_root_path(page)
            # static_path = os.path.join(relative_root_path, 'static')
    
            GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS', 'false').lower() == 'true'
            if GITHUB_ACTIONS and page == 'index.html':
                relative_root_path = './' # 강제로 build폴더없이 루트가 되는 상황이니 ./로 지정
    
            static_path = os.path.join(relative_root_path, 'static')
    ```
    - 이렇게 하면, .io/레포명에서 index.html의 static들이 ./static/으로 잡혀 잘 보이게 된다.
    - 하지만, 다른 페이지들에서는  링크 등이 ../static/으로 잡혀서 -> 클릭시 `도메인 기준` ../static으로 가므로 .io/office/~ 부분이 .io/~로 office가 안먹히게 된다.  

### ~~가비아 서브도메인을 통해 .io/레포명 전체를 root로 인식시키기~~


1. 가비아 > 서비스 관리 > 도메인 관리 > DNS 정보 > `도메인 선택후 DNS 관리`까지 들어가야 서브도메인들이 보인다.
    - 참고) https://is2js.github.io/blog_raw/ 의 깃허브페이지는 `CNAME` + 호스트 `서브도메인명(blog)` + 값/위치 `is2js.github.io.`로 설정되어있다.
        - 즉, 값/위치에는 is2js.github.io.까지만 설정하면 되고, 레포명은 안적어줘도 된다. 특히 `io.`으로 .으로 끝내는 것이 희한하다.
        - app.chojaeseong.com 의 경우, A 레코드로 IP주소를 넣어주는데, 타회사 도메인의 경우, .(dot)으로 끝내는가보다.
2. 레코드 추가 > `CNAME` 선택 후 `office(레포명 or 서브도메인명)`을 .chojaeseong.com(도메인)앞에 위치시키고 값/위치는 `깃허브아이디.github.io`까지만 설정해준다.
3. 이제 우리 github repository > settings > pages에서
    - Custom domain에 `office.chojaeseong.com`을 입력하고 save를 눌러준다.
    - 그러면, CNAME 파일이 없다고 에러가 뜬다. 

- 나는 지금 가비아 도메인 -> aws route 53에서 인증받고 있으므로 aws에서 연결만 해주면 된다.

### 이미 gabia <-> route53 연결 및 certicate 인증된 도메인이라 -> gabia설정 및 DNS A레코드 추가 생략. aws route 53에서만 CNAME 추가
- CNAME을 직접 추가하는게 아니라 aws route 53에서 등록하고 custom domain을 입력시, 알아서 CNAME처리도 된다고 한다.

1. aws route 53 > 호스트 영역 > 해당 도메인 클릭
2. 레코드 생성 > 레코드 유형 `CNAME` 선택. 레코드 이름에는 `서브도메인명`을 입력. 값에는 `깃허브아이디.github.io`만 입력
3. github repo > settings > pages > custom domain에 `서브도메인명.도메인`을 입력 후 save
4. 