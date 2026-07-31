import cv2
import numpy as np

from core.classifier import GraphicClassifier


class GraphicAnalyzer:

    def analyze(self, image_path):

        img = cv2.imread(
            image_path,
            cv2.IMREAD_UNCHANGED
        )

        if img is None:
            raise Exception(
                "Impossibile aprire immagine"
            )

        h, w = img.shape[:2]
        total = h * w

        # ==========================
        # ALPHA
        # ==========================

        alpha = None

        if len(img.shape) == 3 and img.shape[2] == 4:

            alpha = img[:, :, 3]
            rgb = img[:, :, :3]

        else:

            rgb = img

        # ==========================
        # TRASPARENZA
        # ==========================

        if alpha is not None:

            transparent = np.sum(
                alpha < 10
            )

        else:

            transparent = 0

        # ==========================
        # TONI
        # ==========================

        gray = cv2.cvtColor(
            rgb,
            cv2.COLOR_BGR2GRAY
        )

        black = np.sum(
            gray < 35
        )

        white = np.sum(
            gray > 240
        )

        # ==========================
        # COMPLESSITA'
        # ==========================

        edges = cv2.Canny(
            gray,
            80,
            160
        )

        edge_density = (
            np.sum(edges > 0)
            / total
        ) * 100

        preview = cv2.resize(
            rgb,
            (256, 256)
        )

        pixels = preview.reshape(
            (-1, 3)
        )

        color_count = len(
            np.unique(
                pixels,
                axis=0
            )
        )

        # ==========================
        # METRICHE
        # ==========================

        result = {

            "width_px": int(w),

            "height_px": int(h),

            "transparent_area_pct":
                round(
                    float(
                        transparent / total * 100
                    ),
                    2
                ),

            "black_area_pct":
                round(
                    float(
                        black / total * 100
                    ),
                    2
                ),

            "white_area_pct":
                round(
                    float(
                        white / total * 100
                    ),
                    2
                ),

            "edge_density":
                round(
                    float(
                        edge_density
                    ),
                    2
                ),

            "color_count":
                int(
                    color_count
                )
        }

        # ==========================
        # CLASSIFICAZIONE
        # ==========================

        result["graphic_type"] = (
            GraphicClassifier.classify(
                result
            )
        )

        result["recommended_preset"] = (
            GraphicClassifier.preset(
                result["graphic_type"]
            )
        )

        # ==========================
        # AUTO RIP PROFILE
        # ==========================

        gtype = result[
            "graphic_type"
        ]

        if gtype == "Photo/AI Art":

            result["auto_preset"] = (
                "Production"
            )

            result["auto_density"] = 82

            result["auto_choke"] = 0.15
            result["auto_feather"] = 0.60
            result["auto_highlight"] = "ON"

        elif gtype == "Tattoo/Gothic":

            result["auto_preset"] = (
                "Ultra Soft"
            )

            result["auto_density"] = 87

            result["auto_choke"] = 0.30
            result["auto_feather"] = 0.25
            result["auto_highlight"] = "OFF"

        elif gtype == "Vector Logo":

            result["auto_preset"] = (
                "Serigrafico"
            )

            result["auto_density"] = 92

            result["auto_choke"] = 0.45
            result["auto_feather"] = 0.10
            result["auto_highlight"] = "OFF"

        elif gtype == "Vintage/Illustration":

            result["auto_preset"] = (
                "Soft DTF"
            )

            result["auto_density"] = 85

            result["auto_choke"] = 0.25
            result["auto_feather"] = 0.40
            result["auto_highlight"] = "ON"

        else:

            result["auto_preset"] = (
                "Production"
            )

            result["auto_density"] = 85

            result["auto_choke"] = 0.25
            result["auto_feather"] = 0.30
            result["auto_highlight"] = "OFF"

        # ==========================
        # PREFLIGHT DTF
        # ==========================

        warnings = []

        # ==========================
        # LINEE TROPPO SOTTILI
        # ==========================

        thin_lines = cv2.Canny(
            gray,
            80,
            160
        )

        thin_pct = (
            np.sum(
                thin_lines > 0
            )
            /
            total
        ) * 100

        if (
            thin_pct > 4
            and
            edge_density > 1
        ):

            warnings.append(
                "Possibili linee troppo sottili"
            )
            
        # molti dettagli fini

        if edge_density > 8:

            warnings.append(
                "Molti dettagli fini"
            )

        # grafica molto complessa

        if color_count > 25000:

            warnings.append(
                "Grafica molto complessa"
            )

        # contrasto basso

        if (
            result["black_area_pct"] < 5
            and
            result["white_area_pct"] < 5
        ):

            warnings.append(
                "Contrasto basso"
            )

        # possibile sfondo

        if (
            result["transparent_area_pct"] < 5
        ):

            warnings.append(
                "Sfondo probabilmente presente"
            )

        # ==========================
        # DETTAGLI MICROSCOPICI
        # ==========================

        binary = cv2.threshold(
            gray,
            240,
            255,
            cv2.THRESH_BINARY_INV
        )[1]

        num_labels, labels, stats, _ = (
            cv2.connectedComponentsWithStats(
                binary,
                connectivity=8
            )
        )

        tiny_objects = 0

        problem_boxes = []
        
        for i in range(
            1,
            num_labels
        ):

            area = stats[
                i,
                cv2.CC_STAT_AREA
            ]

            width = stats[
                i,
                cv2.CC_STAT_WIDTH
            ]

            height = stats[
                i,
                cv2.CC_STAT_HEIGHT
            ]

            if (
                area < 6
                and
                width < 3
                and
                height < 3
            ):

                tiny_objects += 1
                x = stats[
                    i,
                    cv2.CC_STAT_LEFT
                ]

                y = stats[
                    i,
                    cv2.CC_STAT_TOP
                ]

                w = stats[
                    i,
                    cv2.CC_STAT_WIDTH
                ]

                h = stats[
                    i,
                    cv2.CC_STAT_HEIGHT
                ]
                
                if len(problem_boxes) >= 20:
                    continue
                    
                problem_boxes.append(
                    (
                        x,
                        y,
                        w,
                        h
                    )
                )
        if tiny_objects > 15:

            warnings.append(
                f"{tiny_objects} dettagli molto piccoli"
            )
            
        result["preflight"] = warnings
        
        result["problem_boxes"] = (
            problem_boxes
        )

        return result