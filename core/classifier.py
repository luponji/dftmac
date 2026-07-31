class GraphicClassifier:

    @staticmethod
    def classify(metrics):

        white = metrics["white_area_pct"]
        black = metrics["black_area_pct"]
        colors = metrics["color_count"]
        edges = metrics["edge_density"]

        if colors < 300:
            return "Vector Logo"

        if black > 35:
            return "Tattoo/Gothic"

        if colors > 3000:
            return "Photo/AI Art"

        if edges > 10:
            return "Detailed Illustration"

        return "Standard Graphic"

    @staticmethod
    def preset(graphic_type):

        mapping = {

            "Vector Logo":
                "Serigrafico",

            "Tattoo/Gothic":
                "Production",

            "Photo/AI Art":
                "Ultra Soft",

            "Detailed Illustration":
                "Soft DTF",

            "Standard Graphic":
                "Production"
        }

        return mapping.get(
            graphic_type,
            "Production"
        )