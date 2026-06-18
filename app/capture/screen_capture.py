from __future__ import annotations

from pathlib import Path

from .window_finder import WindowInfo, find_window, window_to_mss_region


def _grab_region(region: dict[str, int], output: str | Path | None = None):
from pathlib import Path

def capture_fullscreen(output: str | Path | None = None):
    try:
        import mss
        from PIL import Image
    except Exception as e:
        raise RuntimeError('화면 캡처에는 mss와 Pillow가 필요합니다.') from e

    if region['width'] <= 0 or region['height'] <= 0:
        raise RuntimeError(f'캡처 영역이 올바르지 않습니다: {region}')

    with mss.mss() as sct:
        img = sct.grab(region)
        pil = Image.frombytes('RGB', img.size, img.rgb)
        if output:
            pil.save(output)
        return pil


def capture_fullscreen(output: str | Path | None = None):
    """마지막 fallback 용 전체 화면 캡처."""

    try:
        import mss
    except Exception as e:
        raise RuntimeError('화면 캡처에는 mss와 Pillow가 필요합니다.') from e

    with mss.mss() as sct:
        return _grab_region(dict(sct.monitors[1]), output)


def capture_window(
    title_keyword: str = "",
    process_name: str = "",
    output: str | Path | None = None,
    client_area_only: bool = True,
):
    """특정 창 제목/프로세스명에 해당하는 창 영역만 캡처한다.

    게임 프로세스 내부 데이터는 읽지 않고, Windows 창 관리자에서 노출하는 창 제목/위치만 사용한다.
    """

    window = find_window(title_keyword=title_keyword, process_name=process_name)
    if not window:
        raise RuntimeError(
            '조건에 맞는 창을 찾지 못했습니다. '
            f'제목 키워드={title_keyword!r}, 프로세스명={process_name!r}'
        )
    return capture_window_info(window, output=output, client_area_only=client_area_only)


def capture_window_info(
    window: WindowInfo,
    output: str | Path | None = None,
    client_area_only: bool = True,
):
    region = window_to_mss_region(window, client_area_only=client_area_only)
    return _grab_region(region, output)


def capture_window_or_fullscreen(
    title_keyword: str = "",
    process_name: str = "",
    output: str | Path | None = None,
    client_area_only: bool = True,
):
    """특정 창 캡처를 먼저 시도하고 실패 시 전체 화면으로 fallback한다."""

    try:
        return capture_window(title_keyword, process_name, output, client_area_only)
    except RuntimeError:
        return capture_fullscreen(output)
    with mss.mss() as sct:
        img=sct.grab(sct.monitors[1])
        pil=Image.frombytes('RGB', img.size, img.rgb)
        if output: pil.save(output)
        return pil

def capture_window_or_fullscreen(title_keyword: str = '', output=None):
    # MVP: 창 탐색 실패 시 전체 화면 캡처 fallback. 창별 캡처는 추후 pywin32로 확장.
    return capture_fullscreen(output)
