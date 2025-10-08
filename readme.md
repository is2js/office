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