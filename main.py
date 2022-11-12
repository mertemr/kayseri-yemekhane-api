import json
from argparse import ArgumentParser, FileType

from api import get_as_json

parser = ArgumentParser()
parser.add_argument(
    "-j",
    "--json",
    type=FileType("w", encoding="UTF-8"),
    help="Veriyi json olarak al, dosya adı girin",
    required=False,
)
parser.add_argument(
    "-c",
    "--color",
    action="store_true",
    default=True,
    help="Renkli çıktı al, Default: True",
)
parser.add_argument("-n", "--no-color", action="store_false", help="Renksiz çıktı al", dest="color")
args = parser.parse_args()

if args.color:
    import colorama

    colorama.initialise.init(autoreset=True)
    R = colorama.ansi.Fore.RED
    G = colorama.ansi.Fore.GREEN
    RE = colorama.ansi.Fore.RESET
else:
    R = G = RE = ""


def main():
    data = get_as_json()

    if args.json:
        args.json.write(json.dumps(data, indent=4, ensure_ascii=False))
        print(f"{args.json.name}'a yazıldı.")
        return

    for i, date, foods in data:
        if i:
            print(f"{G+date+RE} günü ({', '.join(foods)}) var.")
        else:
            print(f"{R+date+RE} günü ({', '.join(foods)}) vardı.")


if __name__ == "__main__":
    main()
