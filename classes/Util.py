class Util:
    def distance(self, x1, y1, x2, y2):
        return ((x1-x2)**2 + (y1-y2)**2)**0.5

    def normalize(self, v1, v2):
        magnitude = self.magnitude(v1, v2)
        return (v1/magnitude, v2/magnitude)
    
    def magnitude(self, v1, v2):
        return (v1**2 + v2**2)**0.5