def get_relative_root_path(post_relative_path, is_test=True):
    """
    외부 배포 말고, 내부에서 빌드할 때 is_test가 들어가서 ../ 갯수 1개 줄이기
    """
    result = ''
    # Get the number of slashes
    num_dirs = len(list(filter(lambda x: len(x) > 0, post_relative_path.split('/'))))

    # 외부일때는 파일1개 index.html -> ../ 필요없이 그자리가 root
    # - 그자리 build폴더가 웹서버의 중심디렉토리가 될 것이기 때문.
    # 내부일 때는 파일1개 index.html -> ../ 의 build 바깥 md_templates 폴더가 root
    if not is_test:
        num_dirs -= 1

    for i in range(num_dirs):
        result += '../'

    # 현재위치일 땐 `./`으로 반환해주기 for 외부실행만.
    if len(result) == 0:
        result = './'

    return result
