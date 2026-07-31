import cv2
import numpy as np


class BlackSaver:

    def process(
        self,
        image,
        preset="Production",
        density=85,
        black_mode="Ink Saver"
    ):

        alpha = None

        if len(image.shape) == 3 and image.shape[2] == 4:

            alpha = image[:, :, 3]
            rgb = image[:, :, :3]

        else:

            rgb = image.copy()

        gray = cv2.cvtColor(
            rgb,
            cv2.COLOR_BGR2GRAY
        )

        result = rgb.copy()

        density_factor = (
            100 - density
        ) / 100.0

        # ==========================
        # PRESET
        # ==========================

        if preset == "Soft DTF":

            threshold = 45
            lift = int(
                10 + (40 * density_factor)
            )

        elif preset == "Ultra Soft":

            threshold = 70
            lift = int(
                22 + (65 * density_factor)
            )

        elif preset == "Serigrafico":

            threshold = 90
            lift = int(
                32 + (80 * density_factor)
            )

        else:  # Production

            threshold = 55
            lift = int(
                15 + (55 * density_factor)
            )

        # ==========================
        # BLACK MASK
        # ==========================

        black_mask = (
            gray < threshold
        )

        edges = cv2.Canny(
            gray,
            60,
            140
        )

        edge_mask = (
            edges > 0
        )

        work_mask = (
            black_mask &
            (~edge_mask)
        )

        # ==========================
        # BLACK HANDLING
        # ==========================

        if black_mode == "Garment Black":

            if alpha is None:

                alpha = np.full(
                    gray.shape,
                    255,
                    dtype=np.uint8
                )

            remove_mask = (
                gray < 25
            )

            alpha[
                remove_mask
            ] = 0

        elif black_mode == "Halftone Black":

            dots = np.random.randint(
                0,
                100,
                gray.shape
            )

            halftone_mask = (
                gray < threshold
            ) & (
                dots > 55
            )

            result[
                halftone_mask
            ] = np.clip(
                result[
                    halftone_mask
                ] + 80,
                0,
                255
            )

        else:  # Ink Saver

            result[
                work_mask
            ] = np.clip(
                result[
                    work_mask
                ] + lift,
                0,
                255
            )

        # ==========================
        # SERIGRAFICO
        # ==========================

        if preset == "Serigrafico":

            dots = np.random.randint(
                0,
                100,
                gray.shape
            )

            perforation = (
                dots > 97
            ) & work_mask

            result[
                perforation
            ] = np.clip(
                result[
                    perforation
                ] + 60,
                0,
                255
            )

        # ==========================
        # ULTRA SOFT
        # ==========================

        if preset == "Ultra Soft":

            blur = cv2.GaussianBlur(
                result,
                (3, 3),
                0
            )

            result = cv2.addWeighted(
                result,
                0.85,
                blur,
                0.15,
                0
            )

        # ==========================
        # ALPHA
        # ==========================

        if alpha is not None:

            result = np.dstack(
                [result, alpha]
            )

        return result

    def estimate_saving(
        self,
        original,
        processed
    ):

        g1 = cv2.cvtColor(
            original[:, :, :3],
            cv2.COLOR_BGR2GRAY
        )

        g2 = cv2.cvtColor(
            processed[:, :, :3],
            cv2.COLOR_BGR2GRAY
        )

        ink1 = np.sum(
            255 - g1.astype(
                np.float32
            )
        )

        ink2 = np.sum(
            255 - g2.astype(
                np.float32
            )
        )

        if ink1 <= 0:
            return 0.0

        saving = (
            (ink1 - ink2)
            / ink1
        ) * 100

        if saving < 0:
            saving = 0

        return round(
            saving,
            2
        )