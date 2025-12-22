class CylinderTechnology:
    """Set cylinders Technology here:"""
    CTDict = {
        'CYLINDER_MAIN' : {
            'OP_1': 'T6-Mazak'
        },
        'CYLINDER_TUBE' : {
            'OP_1': 'T1-Man',
            'OP_2': 'T6-Mazak'
         },
        'CYLINDERS_WELDING' : {
            'OP_1': 'Brygada'
        },
        'FLANGE' : {
            'OP_1': 'Kooperacja',
            'OP_2': 'T4-Fct',
            'OP_3': 'F4-Dmg144'
        },
        'SLEEVE' : {
            'OP_1': 'T4-Fct'
        }
    }

    def __init__(self, draw, stat=1):
        self.draw = draw
        self.draw_type = CylinderPartsNumber.draw_cyinder.get(draw)
        self.tech_route = CylinderTechnology.CTDict.get(self.draw_type)
        self.stat = stat
        self.material = self.material_setter()
        self.comment = self.comment_setter()
        self.tech = [self.tech_route.get(k) for k in self.tech_route.keys()]
        self.pop_done = False
        self.tech_len = len(self.tech)
        self.tech.reverse()

    def cyl_pop(self):
        if not self.tech:
            return 'NULL'
        else:
            if not self.pop_done:
                self.pop_done = True
            return f"'{self.tech.pop()}'"

    def curr_op(self):
        if self.pop_done:
            return "''"
        return f"'{self.tech[- self.stat]}'"

    def material_setter(self):
        result = CylinderPartsNumber.MATERIALS.get(self.draw)
        if not result:
            result = ''
        return result

    def comment_setter(self, ):
        return CylinderPartsNumber.COMMENTS.get(self.draw_type)

    def next_op(self):
        if self.stat >= len(self.tech) or self.pop_done:
            return "''"
        else:
            return f"'{self.tech[- (self.stat + 1)]}'"

class CylinderPartsNumber:

    draw_cyinder = {
        '59711120330': 'SLEEVE',  # CF500
        '59710920491': 'SLEEVE',  # CF1000
        '59711021666': 'SLEEVE',  # CF2000
        '59711021666': 'SLEEVE',  # CF3000
        '59711120328': 'FLANGE',  # CF500
        '59710920489': 'FLANGE',  # CF1000
        '59711021664': 'FLANGE',  # CF2000
        '59711021664': 'FLANGE',  # CF3000
        '59711320582': 'FLANGE',  # CF4000
        '59711120329': 'CYLINDER_TUBE',  # CF500
        '59710920490': 'CYLINDER_TUBE',  # CF1000
        '59711021665': 'CYLINDER_TUBE',  # CF2000
        '59711021675': 'CYLINDER_TUBE',  # CF3000
        '59711320583': 'CYLINDER_TUBE',  # CF4000
        '59711120327': 'CYLINDERS_WELDING',  # CF500
        '59710920488': 'CYLINDERS_WELDING',  # CF1000
        '59711021663': 'CYLINDERS_WELDING',  # CF2000
        '59711021676': 'CYLINDERS_WELDING',  # CF3000
        '59711320581': 'CYLINDERS_WELDING',  # CF4000
        '59711120326': 'CYLINDER_MAIN',  # CF500
        '59710920487': 'CYLINDER_MAIN',  # CF1000
        '59711021662': 'CYLINDER_MAIN',  # CF2000
        '59711021677': 'CYLINDER_MAIN',  # CF3000
        '59711320580': 'CYLINDER_MAIN',  # CF4000
    }
    CYLINDER_SLEEVE = [
        '59711120330',  # CF500
        '59710920491',  # CF1000
        '59711021666',  # CF2000
        '59711021666',  # CF3000
        '59711320584',  # CF4000
        ]
    CYLINDER_FLANGE = [
        '59711120328',  # CF500
        '59710920489',  # CF1000
        '59711021664',  # CF2000
        '59711021664',  # CF3000
        '59711320582',  # CF4000
        ]
    CYLINDERS_TUBE = [
        '59711120329', # CF500
        '59710920490', # CF1000
        '59711021665', # CF2000
        '59711021675', # CF3000
        '59711320583', # CF4000
        ]
    CYLINDERS_WELDING = [
        '59711120327', # CF500
        '59710920488', # CF1000
        '59711021663', # CF2000
        '59711021676', # CF3000
        '59711320581' # CF4000
        ]
    CYLINDERS_MAIN = [
        '59711120326', # CF500
        '59710920487', # CF1000
        '59711021662', # CF2000
        '59711021677', # CF3000
        '59711320580', # CF4000
        '',  #
        ]

    MATERIALS = {
        '59711021664': 'fi330 304L', #FLANGE CFH2000
        '59711021666': 'Ru236/190 304L', #SLEEVE CFH2000
        '59711021665': 'ru218.6x12.25 Nikiel', #TUBE CFH2000
        'TUBE': '',
        'CYLINDERS_WELDING': '',
        'CYLINDER_MAIN': '',
    }

    COMMENTS = {
        'SLEEVE': 'przygotówka z kooperacji',
        'FLANGE': '',
        'TUBE': '',
        'CYLINDERS_WELDING': 'Rysunek Spawalniczy',
        'CYLINDER_MAIN': '',
    }




