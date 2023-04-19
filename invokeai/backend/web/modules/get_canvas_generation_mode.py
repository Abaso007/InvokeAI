from typing import Literal, Union

from PIL import Image, ImageChops
from PIL.Image import Image as ImageType


# https://stackoverflow.com/questions/43864101/python-pil-check-if-image-is-transparent
def check_for_any_transparency(img: Union[ImageType, str]) -> bool:
    if type(img) is str:
        img = Image.open(str)

    if img.info.get("transparency", None) is not None:
        return True
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True
    return False


def get_canvas_generation_mode(
    init_img: Union[ImageType, str], init_mask: Union[ImageType, str]
) -> Literal["txt2img", "outpainting", "inpainting", "img2img",]:
    if type(init_img) is str:
        init_img = Image.open(init_img)

    if type(init_mask) is str:
        init_mask = Image.open(init_mask)

    init_img = init_img.convert("RGBA")

    # Get alpha from init_img
    init_img_alpha = init_img.split()[-1]
    init_img_alpha_mask = init_img_alpha.convert("L")
    init_img_has_transparency = check_for_any_transparency(init_img)

    if init_img_has_transparency:
        init_img_is_fully_transparent = init_img_alpha_mask.getbbox() is None

    """
    Mask images are white in areas where no change should be made, black where changes
    should be made.
    """

    # Fit the mask to init_img's size and convert it to greyscale
    init_mask = init_mask.resize(init_img.size).convert("L")

    """
    PIL.Image.getbbox() returns the bounding box of non-zero areas of the image, so we first
    invert the mask image so that masked areas are white and other areas black == zero.
    getbbox() now tells us if the are any masked areas.
    """
    init_mask_bbox = ImageChops.invert(init_mask).getbbox()
    if init_img_has_transparency:
        return "txt2img" if init_img_is_fully_transparent else "outpainting"
    init_mask_exists = init_mask_bbox is not None

    return "inpainting" if init_mask_exists else "img2img"


def main():
    # Testing
    init_img_opaque = "test_images/init-img_opaque.png"
    init_img_partial_transparency = "test_images/init-img_partial_transparency.png"
    init_img_full_transparency = "test_images/init-img_full_transparency.png"
    init_mask_no_mask = "test_images/init-mask_no_mask.png"
    init_mask_has_mask = "test_images/init-mask_has_mask.png"

    print(
        "OPAQUE IMAGE, NO MASK, expect img2img, got ",
        get_canvas_generation_mode(init_img_opaque, init_mask_no_mask),
    )

    print(
        "IMAGE WITH TRANSPARENCY, NO MASK, expect outpainting, got ",
        get_canvas_generation_mode(init_img_partial_transparency, init_mask_no_mask),
    )

    print(
        "FULLY TRANSPARENT IMAGE NO MASK, expect txt2img, got ",
        get_canvas_generation_mode(init_img_full_transparency, init_mask_no_mask),
    )

    print(
        "OPAQUE IMAGE, WITH MASK, expect inpainting, got ",
        get_canvas_generation_mode(init_img_opaque, init_mask_has_mask),
    )

    print(
        "IMAGE WITH TRANSPARENCY, WITH MASK, expect outpainting, got ",
        get_canvas_generation_mode(init_img_partial_transparency, init_mask_has_mask),
    )

    print(
        "FULLY TRANSPARENT IMAGE WITH MASK, expect txt2img, got ",
        get_canvas_generation_mode(init_img_full_transparency, init_mask_has_mask),
    )


if __name__ == "__main__":
    main()
