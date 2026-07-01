with open("/Users/lorenzomarinolli/lavoro/programmazione_personale/sticker-inventory/figurine.md", "r") as f:
    lines = f.readlines()

total_count = 0
for line in lines:
    line = line.strip()
    # Skip headers like 2011-2012 or empty lines
    if not line or line.startswith('20') or line.startswith('**'):
        continue
    # If the line contains items separated by commas
    parts = line.split(',')
    # Filter empty parts just in case
    parts = [p.strip() for p in parts if p.strip()]
    
    # We might have lists with dashes in the "Figurine fuori ordine" section, let's exclude those.
    if line.startswith('-'):
        continue

    if parts:
        total_count += len(parts)

print(total_count)
