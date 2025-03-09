def get_relative_root_path(post_relative_path):

    result = ''
    # Get the number of slashes
    num_dirs = len(list(filter(lambda x: len(x) > 0, post_relative_path.split('/'))))

    # 외부일때는 파일1개 index.html -> ../ 필요없이 그자리가 root
    # - 그자리 build폴더가 웹서버의 중심디렉토리가 될 것이기 때문.
    # 내부일 때는 파일1개 index.html -> ../ 의 build 바깥 md_templates 폴더가 root
    if __name__ != '__main__':
        num_dirs -= 1

    for i in range(num_dirs):
        result += '../'

    # 현재위치일 땐 `./`으로 반환해주기
    if len(result) == 0:
        result = './'

    return result
