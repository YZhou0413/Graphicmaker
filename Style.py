class Style:
    
    def __init__(self, path, part_name, style_name, real=0):
        self.style_name = style_name
        self.part_name = part_name
        self.path = path 
        self.real = real
        self.brightness = None
        self.hue = None
        self.alpha = None
        self.coordinates = [0, 0]

    def set_color_adjustments(self, hue, saturation, brightness, alpha):
        self.hue = hue
        self.saturation = saturation
        self.brightness = brightness
        self.alpha = alpha

    