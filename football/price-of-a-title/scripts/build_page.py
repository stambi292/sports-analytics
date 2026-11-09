"""Insert data/title_cost.json into template.html -> index.html (standalone) and an artifact copy."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
t = (ROOT / "template.html").read_text(encoding="utf-8")
d = json.loads((ROOT / "data" / "title_cost.json").read_text(encoding="utf-8"))
page = t.replace("/*__DATA__*/{}", json.dumps(d, separators=(",", ":"), ensure_ascii=False))
head = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n')
i = page.index('<header class="mast">')
(ROOT / "index.html").write_text(head + page[:i] + "</head>\n<body>\n" + page[i:] + "\n</body>\n</html>\n", encoding="utf-8")
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(page, encoding="utf-8")
print("built")
