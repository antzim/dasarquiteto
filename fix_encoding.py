"""
The files have been double-encoded:
- Original: UTF-8 text (e.g., 'ã' = bytes c3 a3)
- These bytes were read as cp1252 (c3='Ã', a3='£') -> 'Ã£'
- Then saved as UTF-8: Ã=c3 83, £=c2 a3 -> bytes c3 83 c2 a3

Fix: read file bytes -> decode as utf-8 -> encode as cp1252 -> decode as utf-8

The tricky part is that some sequences like em-dash (e2 80 94) when read as cp1252:
  e2='â', 80='€' (cp1252), 94='"' (cp1252)
  -> 'â€"' which encodes to c3 a2 e2 82 ac e2 80 9d in UTF-8

So we need: read as utf-8, encode as cp1252, decode as utf-8
"""

def fix_double_encoding(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    # Strip BOM if present
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    
    # The file is valid UTF-8 but characters are double-encoded
    # i.e., what we have is utf8(cp1252(original_utf8_bytes))
    # To fix: decode as utf-8, encode as cp1252, decode as utf-8
    
    # Step 1: decode current utf-8 (get the cp1252 chars)
    text = raw.decode('utf-8', errors='replace')
    
    # Step 2: encode as cp1252 (restore original bytes)
    # Use surrogatepass to handle any oddities
    try:
        original_bytes = text.encode('cp1252', errors='replace')
    except Exception as e:
        print(f"cp1252 encode failed: {e}")
        return False
    
    # Step 3: decode as utf-8 (get proper text)
    fixed = original_bytes.decode('utf-8', errors='replace')
    
    # Count accents to verify
    accent_chars = 'ãõáéíóúâêîôûàçÃÕÁÉÍÓÚÂÊÎÔÛÀÇñÑ'
    before = sum(1 for c in text if c in accent_chars)
    after = sum(1 for c in fixed if c in accent_chars)
    garbled = text.count('Ã') + text.count('â€')
    garbled_after = fixed.count('Ã') + fixed.count('â€')
    
    print(f"{filepath}:")
    print(f"  Acentos validos: {before} -> {after}")
    print(f"  Texto corrompido: {garbled} -> {garbled_after}")
    
    words_check = ['não', 'são', 'ção', 'portfólio', 'coleção', 'técnica', 'Arquitetura']
    found = [w for w in words_check if w in fixed]
    print(f"  Palavras corretas: {found}")
    
    # Save
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(fixed)
    print(f"  [SALVO]")
    print()
    return True

fix_double_encoding('index.html')
fix_double_encoding('portfolio.html')
