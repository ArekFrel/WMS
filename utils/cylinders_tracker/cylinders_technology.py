from wms_main.confidential import CylinderPartsNumber

class CylinderTechnology:
    """Set cylinders Technology here:"""
    CTDict = {
        'CYLINDER_MAIN': {
            'OP_1': 'T1-Man',
            'OP_2': 'T6-Mazak',
            'OP_3': 'Quality',
            'OP_4': 'Brygada',
            'OP_5': 'Quality',
            'OP_6': 'T6-Mazak',
            'OP_7': 'Szlif-Cylinder',
            'OP_8': 'Quality',
            'OP_9': 'Kooperacja',
            'OP_10': 'Quality'
        },
        'CYLINDER_HONING': {
            'OP_1': 'Brygada'
        },
        'FLANGE' : {
            'OP_1': 'Kooperacja',
            'OP_2': 'T4-Fct',
            # 'OP_3': 'F4-Dmg144', #zmiana technologii wykonania
            'OP_3': 'Quality'#dodano 20/04/2025
        },
        'SLEEVE' : {
            'OP_1': 'T4-Fct',
            'OP_2': 'Quality'#dodano 20/04/2025
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
        comment = CylinderPartsNumber.COMMENTS.get(self.draw_type)
        if not comment:
            return ''
        else:
            return comment

    def next_op(self):
        if self.stat >= len(self.tech) or self.pop_done:
            return "''"
        else:
            return f"'{self.tech[- (self.stat + 1)]}'"







