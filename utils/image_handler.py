from PIL import Image
import os

class ImageHandler:
    def get_image_paths(self, directory, supported_extensions=('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        """Load all images from a directory."""
        if not os.path.exists(directory):
            return []

        images = [f for f in os.listdir(directory) if f.lower().endswith(supported_extensions)]
        return [os.path.join(directory, img) for img in images]

    def resize_image(self, image, size=(400, 300)):
        """Resize the currently loaded image."""
        if image:
            return image.resize(size, Image.LANCZOS)
        return None
    
    def resize_image_with_aspect_ratio(self, image, max_width=400, max_height=300):
        if image:
            # Get original dimensions
            width, height = image.size
            
            # Calculate the aspect ratio
            aspect_ratio = width / height
            
            # Check if the image needs to be resized
            if width > max_width or height > max_height:
                # Calculate new dimensions while maintaining the aspect ratio
                if aspect_ratio > 1:  # Wider than tall
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:  # Taller than wide
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
            else:
                # If the image is within the max dimensions, amplify it
                if aspect_ratio > 1:  # Wider than tall
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                    if new_height < max_height:  # Adjust to fit max_height if necessary
                        new_height = max_height
                        new_width = int(max_height * aspect_ratio)
                else:  # Taller than wide
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)
                    if new_width < max_width:  # Adjust to fit max_width if necessary
                        new_width = max_width
                        new_height = int(max_width / aspect_ratio)

            return image.resize((new_width, new_height), Image.ANTIALIAS)
        return None