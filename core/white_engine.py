import cv2
import numpy as np


class WhiteEngine:

    def prepare_for_rip(
        self,
        image,
        choke=0.25,
        feather=0.50
    ):

        # Se non c'è alpha
        if len(image.shape) < 3:
            return image

        if image.shape[2] != 4:
            return image

        alpha = image[:, :, 3]

        kernel_size = max(
            1,
            int(choke * 4)
        )

        kernel = np.ones(
            (
                kernel_size,
                kernel_size
            ),
            np.uint8
        )

        alpha = cv2.erode(
            alpha,
            kernel,
            iterations=1
        )

        blur_size = max(
            1,
            int(feather * 4)
        )

        if blur_size % 2 == 0:
            blur_size += 1

        if blur_size > 1:

            alpha = cv2.GaussianBlur(
                alpha,
                (
                    blur_size,
                    blur_size
                ),
                0
            )

        result = image.copy()

        result[:, :, 3] = alpha

        return result