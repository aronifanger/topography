from shapely.geometry import Polygon, Point
from shapely.affinity import scale, translate, affine_transform

class PolyScaler:
    def __init__(self):
        self.scale_x = None
        self.scale_y = None
        self.translation_x = None  # Valor de translação em x
        self.translation_y = None  # Valor de translação em y

    def fit(self, polygon: Polygon):
        minx, miny, maxx, maxy = polygon.bounds
        original_width = maxx - minx
        original_height = maxy - miny
        target_width = 18  # Since we are rescaling between (1, 1) and (19, 19)
        target_height = 18
        self.scale_x = target_width / original_width
        self.scale_y = target_height / original_height
        self.translation_x = 1 - minx * self.scale_x
        self.translation_y = 1 - miny * self.scale_y
        return self

    def transform(self, polygon: Polygon):
        if self.scale_x is None or self.scale_y is None:
            raise ValueError("Scaler has not been fitted yet.")
        scaled_polygon = scale(polygon, xfact=self.scale_x, yfact=self.scale_y, origin=(0, 0))
        translated_polygon = translate(scaled_polygon, xoff=self.translation_x, yoff=self.translation_y)
        return translated_polygon

    def inverse_transform(self, polygon: Polygon):
        if self.scale_x is None or self.scale_y is None:
            raise ValueError("Scaler has not been fitted yet.")
        translated_polygon = translate(polygon, xoff=-self.translation_x, yoff=-self.translation_y)
        scaled_polygon = scale(translated_polygon, xfact=1/self.scale_x, yfact=1/self.scale_y, origin=(0, 0))
        return scaled_polygon
    
    def transform_point(self, point: Point):
        if self.scale_x is None or self.scale_y is None:
            raise ValueError("Scaler has not been fitted yet.")
        # Escalamos e transladamos o ponto de forma direta, sem criar um novo objeto Point.
        scaled_x = point.x * self.scale_x + self.translation_x
        scaled_y = point.y * self.scale_y + self.translation_y
        return Point(scaled_x, scaled_y)

    def inverse_transform_point(self, point: Point):
        if self.scale_x is None or self.scale_y is None:
            raise ValueError("Scaler has not been fitted yet.")
        # Revertendo a escala e a translação do ponto.
        original_x = (point.x - self.translation_x) / self.scale_x
        original_y = (point.y - self.translation_y) / self.scale_y
        return Point(original_x, original_y)

# Uso da classe PolyScaler:
if __name__ == "__main__":
    # Original polygon example
    original_polygon = Polygon([(2, 2), (2, 8), (8, 8), (8, 2)])
    
    # Original point example
    original_point = Point(5, 5)
    
    # Creating PolyScaler object and fitting it to the original polygon
    scaler = PolyScaler()
    scaler.fit(original_polygon)
    
    # Transforming polygon and point
    transformed_polygon = scaler.transform(original_polygon)
    transformed_point = scaler.transform_point(original_point)
    
    # Inversing the transformations
    inverse_transformed_polygon = scaler.inverse_transform(transformed_polygon)
    inverse_transformed_point = scaler.inverse_transform_point(transformed_point)

    print(f"Original Polygon: {original_polygon}")
    print(f"Transformed Polygon: {transformed_polygon}")
    print(f"Inverse Transformed Polygon: {inverse_transformed_polygon}")
    print(f"Original Point: {original_point}")
    print(f"Transformed Point: {transformed_point}")
    print(f"Inverse Transformed Point: {inverse_transformed_point}")