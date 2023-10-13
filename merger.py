import os
import fitz
from stat import S_IWRITE
catalog = 'C:\Dokumenty\sat'

for file in os.listdir(catalog):

    if not file.lower().endswith('.pdf') or file.endswith('merged.pdf'):
        continue
    doc_path = os.path.join(catalog, file)
    merged_doc = os.path.join(catalog, 'merged.pdf')
    save_doc = os.path.join(catalog, 'merged_temp.pdf')
    with fitz.open(doc_path) as doc:
        try:
            if 'merged.pdf' not in os.listdir(catalog):
                doc.save(merged_doc)
                os.chmod(merged_doc, S_IWRITE)
            else:
                with fitz.open(merged_doc) as doc_merged:
                    doc_merged.insert_file(doc)
                    doc_merged.save(save_doc)
                    os.chmod(save_doc, S_IWRITE)
                os.remove(merged_doc)
                os.rename(save_doc, merged_doc)
        except PermissionError:
            print(f'Brak dostępu do pliku {merged_doc}')


