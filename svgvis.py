from fract import float_of_fract

class SVGFigure:
    def __init__(self, slot, color, linesegs, msg=None, msg_size=55):
        self.xmin = 0
        self.xmax = 1
        self.ymin = 0
        self.ymax = 1
        self.slot = slot
        self.linesegs = [(l[0],l[1],color) for l in linesegs]
        self.msg = msg
        self.msg_size = msg_size

    def svgLine(self,l):
        a = l[0]
        b = l[1]
        return '<line stroke="%s" stroke-width="2" x1="%s" y1="%s" x2="%s" y2="%s"/>' % (l[2], float_of_fract(a[0], self.sx, self.sscale), float_of_fract(a[1], self.sy, self.sscale), float_of_fract(b[0], self.sx, self.sscale), float_of_fract(b[1], self.sy, self.sscale))

    def draw(self):        
        for seg in self.linesegs:
            for pt in [seg[0], seg[1]]:
                self.xmin = min(self.xmin, pt[0])
                self.xmax = max(self.xmax, pt[0])
                self.ymin = min(self.ymin, pt[1])
                self.ymax = max(self.ymax, pt[1])

        self.sscale = 500 / max(self.xmax - self.xmin, self.ymax - self.ymin)
        self.sx = (self.slot * 500 + (self.slot + 1) * 70) - (self.sscale * self.xmin)
        self.sy = 70 - (self.sscale * self.ymin)

        svg = '\n'.join([self.svgLine(l) for l in self.linesegs])
        if self.msg:
            svg += '<text x="%d" y="%d" font-family="Verdana" font-size="%d">%s</text>' % (self.sx, self.sy + 300, self.msg_size, self.msg)
        return svg

    def addSubfigure(self,color,fig):
        self.linesegs.extend([(f[0],f[1],color) for f in fig])

class SVGGallery:
    def __init__(self):
        self.figures = []
                         
    def addFigure(self, color, linesegs, msg=None, msg_size=55):
        slot = len(self.figures)
        fig = SVGFigure(slot, color, linesegs, msg, msg_size)
        self.figures.append(fig)
        return fig

    def appendFigure(self,color, linesegs):
        slot = len(self.figures) - 1
        self.figures[slot].addSubfigure(color, linesegs)

    def draw(self):
        bodies = map(lambda x: x.draw(), self.figures)
        width = (len(self.figures) * 500 + (len(self.figures) + 1) * 70)
        res = [
            '<?xml version="1.0" encoding="iso-8859-1"?>',
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" height="640" width="%s" viewBox="0 0 %s 640">' % (width, width)] + bodies + ['</svg>']
        return '\n'.join(res)

