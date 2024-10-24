class PbTech:

    """Set pb_technology here:"""
    OP_1 = 'F5-MAZ200'
    OP_2 = 'F7-Cheto'
    OP_3 = 'F5-MAZ200'
    OP_4 = 'F7-Cheto'
    OP_5 = 'Quality'

    def __init__(self):
        self.tech = [PbTech.OP_5,
                     PbTech.OP_4,
                     PbTech.OP_3,
                     PbTech.OP_2,
                     PbTech.OP_1
                     ]

    def pb_op(self):
        if not self.tech:
            return None
        else:
            return self.tech.pop()




