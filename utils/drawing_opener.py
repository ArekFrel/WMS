import os
import pyperclip
import time


def main():
    # parent = 'C:/VaultWork/Designs/Contracts/Production documentation'
    parent = '\\\\PLOLFPS01.tp1.ad1.tetrapak.com\\PUBLIC\\!!__PRODUKCJA__!!\\IE\Rysunki\\PDFs'
    # order = input('NUMER ZLECENIA: ')
    print("Monitoring schowka... (naciśnij Ctrl+C, aby zakończyć)")
    # W:\!!__PRODUKCJA__!!\IE\Rysunki\PDFs
    try:
        last_text = pyperclip.paste()
        while True:
            current_text = pyperclip.paste()
            if current_text != last_text:  # Jeśli zawartość schowka się zmieniła
                drawing = f"{current_text}.pdf"
                main_path = os.path.join(parent, drawing)
                try:
                    os.startfile(main_path, 'open')
                except FileNotFoundError:
                    print(f'{main_path}  -- nof found.')
                print(f"{current_text}")
                last_text = current_text
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nZakończono monitorowanie schowka.")


if __name__ == '__main__':
    main()
