import re

name = '1999999 SAP.pdf'

print(bool(re.search(r"\d{7} .*[.]pdf", name)))
