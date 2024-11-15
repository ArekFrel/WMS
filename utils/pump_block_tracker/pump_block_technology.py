class PbTech:

    """Set pb_technology here:"""
    TECH_DICT = {
        'OP_1': 'F5-Maz200',
        'OP_2': 'F7-Cheto',
        'OP_3': 'F5-Maz200',
        'OP_4': 'Szlif-PB',
        'OP_5': 'Quality',
        'OP_6': 'Rework-PB',
        'OP_7': 'Mycie-PB',
        'OP_8': 'Quality-FIN',
        'OP_9': 'Wysyłka'
    }

    def __init__(self, stat=1):
        self.stat = stat
        self.tech = [PbTech.TECH_DICT.get(k) for k in PbTech.TECH_DICT.keys()]
        self.pop_done = False
        self.tech_len = len(self.tech)
        self.tech.reverse()

    def pb_pop(self):
        if not self.tech:
            return 'NULL'
        else:
            if not self.pop_done:
                self.pop_done = True
            return f"'{self.tech.pop()}'"

    def curr_op(self):
        if self.pop_done:
            return ''
        return f"'{self.tech[- self.stat]}'"

    def next_op(self):
        if self.stat >= len(self.tech) or self.pop_done:
            return ''
        else:
            return f"'{self.tech[- (self.stat + 1)]}'"

    def prev_op(self):
        if self.stat == 1 or self.pop_done:
            return ''
        else:
            return self.tech[- (self.stat - 1)]


def main():
    pass


if __name__ == '__main__':
    main()
