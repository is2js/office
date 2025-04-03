import re
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
import xml.etree.ElementTree as etree


class YouTubeEmbedPattern(Pattern):
    """Markdown 패턴을 찾아 <iframe> 태그로 변환"""

    def __init__(self, pattern):
        super().__init__(pattern)

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
        # height = has_height or ("auto" if video_type == 'youtube' else "100%")  # 기본값 유튭 auto / 쇼츠 100%

        # 쇼츠 URL과 일반 URL 구분
        # if video_type == "shorts":
        #     video_url = f"https://www.youtube.com/embed/{video_id}?playlist={video_id}&loop=1"
        # else:
        # video_url = f"https://www.youtube.com/embed/{video_id}?controls=0&showinfo=0&rel=0&modestbranding=0&playsinline=0"
        video_url = f"https://www.youtube.com/embed/{video_id}?controls=0&modestbranding=1&rel=0&playsinline=1&fs=0&cc_load_policy=0&iv_load_policy=3&autoplay=0&mute=0&showinfo=0"

        # width 숫자 추출 (100, 50, 30 등)
        if has_width:
            match_width = re.match(r"(\d+)(px|em|rem|%)", width)
            width_value = int(match_width.group(1)) if match_width else 100
            width_unit = match_width.group(2) if match_width else ""

        # height 숫자 추출 (px 또는 % 사용 가능)
        if has_height:
            match_height = re.match(r"(\d+)(px|em|rem|%)", height)
            height_value = match_height.group(1) if match_height else "auto"
            height_unit = match_height.group(2) if match_width else ""

        # height가 지정된 경우, width는 aspect-ratio에 따라 height 비례값으로 설정
        # if height_value != "auto":
        #     if self.video_type == "youtube":
        #         width_value = height_value * 16 / 9
        #     else:
        #         width_value = height_value * 9 / 16

        # display 설정
        # - 유튜브가 50% 이하 or
        # is_inline = video_type == 'youtube ' and width_value <= 50  or (
        #         video_type == 'shorts ' and width_value <= 50  # 유튜브가 50% 이하면 inline
        # )
        # display_style = "inline-block" if match_width or is_inline else "block"

        # <iframe> 태그 생성
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

        # video_type에 따라 aspect-ratio 속성을 다르게 설정
        if video_type == "youtube":
            aspect_ratio = "16 / 9"
        else:
            aspect_ratio = "9 / 16"

        # iframe.set("style", f"aspect-ratio: {aspect_ratio}; display: {display_style};")
        iframe.set("style", f"aspect-ratio: {aspect_ratio}; max-width:100%; display: block; margin: 0 auto;")

        iframe.set("allow", "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture")
        iframe.set("frameborder", "0")
        iframe.set("allowfullscreen", "true")

        # 부모는 걍 100% 가운데정렬하는 flex div
        div = etree.Element("div")
        div.set("class", "youtube" if video_type == "youtube" else "shorts")
        # div.set("style", f"display: {display_style};  text-align: center; aspect-ratio: {aspect_ratio}; width: {width}; height: {height_value};")
        div.set("style",
                f"display: flex;  flex-wrap:wrap; justify-content: center; align-items: center; margin = 0.5em auto; width: 100%;")
        # div.set("style", f"display: {display_style}; text-align: center;")
        # div.set("data-inline", "true" if is_inline else "false")  # ✅ inline 여부 표시
        div.append(iframe)

        return div


class YouTubeEmbedExtension(Extension):
    """Markdown 확장 기능"""

    # YOUTUBE_PATTERN = r'<(youtube|shorts) id="(?P<id>[^"]+)"(?: width="(?P<width>[^"]+)")?(?: height="(?P<height>[^"]+)")?>'

    # YOUTUBE_PATTERN = r'<(?P<type>youtube|shorts) id="(?P<id>[\w-]+)"(?:\s+width="(?P<width>[\d%px]+)")?(?:\s+height="(?P<height>[\d%px]+)")?\s*/?>'
    YOUTUBE_PATTERN = r'<(?P<type>youtube|shorts) id="(?P<id>[\w-]+)"(?:\s+(?:width="(?P<width>[\d%px]+)"|height="(?P<height>[\d%px]+)")){0,2}\s*/?>'

    def extendMarkdown(self, md):
        # YOUTUBE_PATTERN = r'<youtube id="(?P<id>[\w-]+)"(?:\s+width="(?P<width>[\d%px]+)")?(?:\s+height="(?P<height>[\d%px]+)")?\s*/?>'
        # SHORTS_PATTERN = r'<shorts id="(?P<id>[\w-]+)"(?:\s+width="(?P<width>[\d%px]+)")?(?:\s+height="(?P<height>[\d%px]+)")?\s*/?>'

        # md.inlinePatterns.register(YouTubeEmbedPattern(YOUTUBE_PATTERN, "youtube"), "youtube_embed", 175)
        # md.inlinePatterns.register(YouTubeEmbedPattern(SHORTS_PATTERN, "shorts"), "shorts_embed", 174)  # 우선순위 낮춤
        md.inlinePatterns.register(YouTubeEmbedPattern(self.YOUTUBE_PATTERN), "youtube_shorts", 175)
