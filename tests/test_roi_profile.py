from app.vision.roi_profile import DEFAULT_PARTY_ROI_PROFILE, NormalizedROI


def test_normalized_roi_scales_to_pixels():
    assert NormalizedROI(0.1, 0.2, 0.3, 0.4).to_pixels((1000, 500)) == (100, 100, 400, 300)
    assert len(DEFAULT_PARTY_ROI_PROFILE.slots) == 6
    assert DEFAULT_PARTY_ROI_PROFILE.slot(1).ability_fields['pokemon_name']
