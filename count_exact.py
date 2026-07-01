with open("/Users/lorenzomarinolli/lavoro/programmazione_personale/sticker-inventory/figurine.md", "r") as f:
    lines = f.readlines()

total = 0
for i, line in enumerate(lines):
    line = line.strip()
    if not line or line.startswith('20') or line.startswith('**') or line.startswith('-'):
        continue
    parts = [p for p in line.split(',') if p.strip()]
    if parts:
        print(f"Line {i+1}: {len(parts)} stickers")
        total += len(parts)

print(f"Total: {total}")
