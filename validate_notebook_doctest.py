#!/usr/bin/env python3
# validate_notebook_doctest.py

import json
import sys
import doctest

def notebook_to_doctest(nb_json):
    """
    Transforme les cellules de code + leurs sorties stream
    en exemples doctest, en gérant correctement les blocs multi‐lignes.
    """
    lines = []
    for cell in nb_json.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        src = ''.join(cell.get('source', [])).rstrip()
        if not src:
            continue

        # On parcourt les lignes du code en suivant la profondeur de parenthèses
        paren_depth = 0
        for raw in src.splitlines():
            stripped = raw.lstrip()
            # calcul de la profondeur de parenthèses pour savoir si c'est une continuation
            paren_depth += raw.count('(') - raw.count(')')
            if paren_depth > 0 or raw.startswith((' ', '\t')):  
                # continuation
                lines.append(f'... {stripped}')
            else:
                # début de bloc / ligne simple
                lines.append(f'>>> {stripped}')
        # sorties 'stream'
        for output in cell.get('outputs', []):
            if output.get('output_type') == 'stream':
                text = ''.join(output.get('text', [])).rstrip('\n')
                for l in text.splitlines():
                    lines.append(l)
        lines.append('')  # séparation entre cellules
    return '\n'.join(lines)

def main(path):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    test_src = notebook_to_doctest(nb)

    parser = doctest.DocTestParser()
    test = parser.get_doctest(
        test_src,
        globs={},
        name=path,
        filename=path,
        lineno=0
    )

    runner = doctest.DocTestRunner()
    result = runner.run(test)
    runner.summarize(verbose=True)

    failed = result.failed
    attempted = result.attempted
    print(f"\nDoctest: {attempted} exemples, {failed} échecs")
    sys.exit(bool(failed))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python validate_notebook_doctest.py <notebook.json>")
        sys.exit(1)
    main(sys.argv[1])
