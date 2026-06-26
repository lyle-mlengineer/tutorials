from schemas import ImageLabelRequest, ImageLabelResponse


class ImageLabellingService:
    def __init__(self):
            pass
    
    def label_image(self, label_request: ImageLabelRequest) -> ImageLabelResponse:
        return "label"
    
    def get_next_image(self) -> str:
        return "example.jpeg"