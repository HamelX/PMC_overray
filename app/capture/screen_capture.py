from pathlib import Path

def capture_fullscreen(output: str | Path | None = None):
    try:
        import mss
        from PIL import Image
    except Exception as e:
        raise RuntimeError('화면 캡처에는 mss와 Pillow가 필요합니다.') from e
    with mss.mss() as sct:
        img=sct.grab(sct.monitors[1])
        pil=Image.frombytes('RGB', img.size, img.rgb)
        if output: pil.save(output)
        return pil

def capture_window_or_fullscreen(title_keyword: str = '', output=None):
    # MVP: 창 탐색 실패 시 전체 화면 캡처 fallback. 창별 캡처는 추후 pywin32로 확장.
    return capture_fullscreen(output)
