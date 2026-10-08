import numpy as np
from airdrum.preprocess import bgr_to_hsv, bgr_to_rgb, gaussian_blur, mirror_frame


def test_mirror_frame_reverses_columns():
    # 2x2 test image where left column is 10, right column is 20
    test_frame = np.array([[[10, 10, 10], [20, 20, 20]], [[10, 10, 10], [20, 20, 20]]], dtype=np.uint8)
    mirrored = mirror_frame(test_frame)

    # First column of mirrored frame should now contain 20
    assert mirrored[0, 0, 0] == 20
    assert mirrored[0, 1, 0] == 10


def test_color_space_conversions_shape():
    dummy_bgr = np.zeros((100, 100, 3), dtype=np.uint8)
    dummy_bgr[:, :, 0] = 255  # Pure blue

    rgb = bgr_to_rgb(dummy_bgr)
    hsv = bgr_to_hsv(dummy_bgr)

    assert rgb.shape == (100, 100, 3)
    assert hsv.shape == (100, 100, 3)
    # Red channel in RGB should be 0, Blue channel in RGB should be 255
    assert rgb[0, 0, 0] == 0
    assert rgb[0, 0, 2] == 255