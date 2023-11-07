from const import CURSOR
from pyodbc import OperationalError

dict_of_quotes = {
	'POMOC NA LASERZE': 'Laser_pomoc',
	'CIĘCIE NA LASERZE': 'Laser_cięcie',
	'CIECIE NA PILACH': 'Piły_cięcie',
	'TOCZENIE': 'Toczenie',
	'FREZOWANIE': 'Frezowanie',
	'GWINTOWANIE': 'Gwintowanie',
	'GOTOWANIE PLASTIKOW': 'Gwintowanie_Plastików',
	'CIEClE NA FISHERZE': 'Cięcie_na_Fisherze',
	'CIECIE PLYT PLASTIKOWYCH': 'Cięcie_Płyt_Plastikowych',
	'SPAWANIE': 'Spawanie',
	'PRZYGOTOWANIE DO SPAWANIA, SZCZEPIANIE': 'Przygotowanie_do_Spawania',
	'ZGNIATANIE SPOIN': 'Zgniatanie_Spoin',
	'SPAWANIE ORBITALNE': 'Spawanie_Orbitalne',
	'SZLIFOWANIE RECZNE': 'Szlifowanie_Ręczne',
	'WIERCENIE I GWINTOWANIE TERMICZNE': 'Wier_i_Gwint_Term',
	'ROZTLACZANIE PLASZCZY': 'Roztlaczanie_Płaszczy',
	'ORGANIZACJA': 'Organizacja',
	'WYCIAGANIE': 'Wyciąganie',
	'MONTAZ': 'Montaż',
	'PROSTOWANIE': 'Prostowanie',
	'DEMONTAZ': 'Demontaż',
	'WYOBLANIE': 'Wyoblanie',
	'CIECIE NA GILOTYNIE': 'Gilotyna_Cięcie',
	'WALCOWANIE': 'Walcowanie',
	'POMOC NA GIECIU': 'Gięcie_Pomoc',
	'GIECIE NA PRASIE KRAWEDZIOWEJ': 'Giecie_Kraw',
	'SZLIFOWANIE AUTOMATYCZNE': 'Szlif_AUTO',
	'SPAWANIE AUTOMATYCZNE': 'Spaw_AUTO',
	'PIASKOWANIE': 'Pisakowanie',
	'WYTWARZANIE SZAF ELEKTRYCZNYCH': 'Szafy_elektryczne',
	'OKABLOWANIE ELEKTRYCZNE': 'Okablowanie',
	'BUFOR CZASOWY': 'Bufor',
	'KONTROLA JAKOSCI - Brig_': 'Quality_Brig',
	'TESTY, FAT': 'Testy',
	'PAKOWANIE': 'Pakowanie',
	'DOKONCZENIE W TETRAPAK': 'Dokończenie'
}

list_of_operations = [v for v in dict_of_quotes.values()]


def main():
	query = f'CREATE TABLE dbo.Quotation (' \
			f'drawing_number VARCHAR(32) NOT NULL UNIQUE, '
	for value in dict_of_quotes.values():
		added_text = f'{value} DECIMAL(7,2), \n'
		query = query + added_text
	query = query + f'Primary Key (drawing_number));'
	with CURSOR:
		try:
			CURSOR.execute(query)
			CURSOR.commit()
			pass
		except OperationalError:
			print('Unknown Error')
			return False


if __name__ == '__main__':
	main()

