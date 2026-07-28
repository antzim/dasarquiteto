import re

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Clean double replacements
    content = content.replace('\ufffdÁrea', 'Área')
    content = content.replace('\ufffdÁgora', 'Ágora')
    content = content.replace('AÁrea', 'Área')
    content = content.replace('ÁÁrea', 'Área')
    content = content.replace('\ufffd', '')

    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

    print(f"Cleaned {filepath}")

clean_file('index.html')
clean_file('portfolio.html')
