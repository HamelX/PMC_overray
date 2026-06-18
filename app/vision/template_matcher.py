def match_template(image_path, template_path, threshold=0.85):
    try:
        import cv2
    except Exception as e:
        raise RuntimeError('템플릿 매칭에는 opencv-python이 필요합니다.') from e
    img=cv2.imread(str(image_path)); tpl=cv2.imread(str(template_path))
    if img is None or tpl is None: return []
    res=cv2.matchTemplate(img, tpl, cv2.TM_CCOEFF_NORMED)
    ys, xs = (res >= threshold).nonzero()
    h,w=tpl.shape[:2]
    return [{'x':int(x),'y':int(y),'w':w,'h':h,'score':float(res[y,x])} for y,x in zip(ys,xs)]
