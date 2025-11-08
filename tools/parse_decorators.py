import re
from pathlib import Path
from typing import List, Tuple

p = Path(r"c:\Users\sebas\Documents\MCP_OUtils\blender-mcp\copy_server.py")
text = p.read_text(encoding='utf-8')
lines = text.splitlines()

# Each tuple: (decorator, func_name, signature, def_line_no, doc_summary)
results: List[Tuple[str, str, str, int, str]] = []

i = 0
from pathlib import Path
from typing import List, Tuple

p = Path(r"c:\Users\sebas\Documents\MCP_OUtils\blender-mcp\copy_server.py")
text = p.read_text(encoding="utf-8")
lines = text.splitlines()

# Each tuple: (decorator, func_name, signature, def_line_no, doc_summary)
results: List[Tuple[str, str, str, int, str]] = []

i = 0
from pathlib import Path
from typing import List, Tuple

p = Path(r"c:\Users\sebas\Documents\MCP_OUtils\blender-mcp\copy_server.py")
text = p.read_text(encoding="utf-8")
lines = text.splitlines()

# Each tuple: (decorator, func_name, signature, def_line_no, doc_summary)
results: List[Tuple[str, str, str, int, str]] = []

i = 0
while i < len(lines):
    from pathlib import Path
    from typing import List, Tuple

    # Small utility that extracts @mcp.tool / @mcp.prompt functions and prints a
    # Markdown table with: decorator, function name, signature, definition line,
    # and the first non-empty docstring line (if present).

    P = Path(r"c:\Users\sebas\Documents\MCP_OUtils\blender-mcp\copy_server.py")
    text = P.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Each tuple: (decorator, func_name, signature, def_line_no, doc_summary)
    results: List[Tuple[str, str, str, int, str]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("@mcp.tool") or stripped.startswith("@mcp.prompt"):
            decorator = stripped
            # find next non-empty line that starts with def
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("def "):
                j += 1
            if j >= len(lines):
                i = j
                continue
            def_line = lines[j]
            # compute def line number (1-indexed)
            def_line_no = j + 1

            # extract function name and possibly multi-line signature
            header_lines: List[str] = [def_line.rstrip()]
            if "(" in def_line and ")" not in def_line:
                k = j + 1
                while k < len(lines):
                    header_lines.append(lines[k].rstrip())
                    if ")" in lines[k]:
                        break
                    k += 1

            header = " ".join(h.lstrip() for h in header_lines)
            m = re.match(r"\s*def\s+([A-Za-z_0-9]+)\s*\((.*)\)\s*(?:->\s*([^:]+))?:\s*$", header)
            if m:
                func_name = m.group(1)
                signature = m.group(2).strip()
            else:
                func_name = "(unknown)"
                signature = ""

            # find docstring: next significant triple-quoted string after def
            k = j + 1
            doc_summary: str = ""
            while k < len(lines):
                l = lines[k].lstrip()
                if l.startswith('"""') or l.startswith("'''"):
                    quote = l[:3]
                    if l.count(quote) >= 2 and len(l) > 3:
                        inner = l.strip()[3:-3].strip()
                        doc_summary = inner.splitlines()[0] if inner else ""
                        break
                    mlines: List[str] = []
                    k += 1
                    while k < len(lines) and quote not in lines[k]:
                        mlines.append(lines[k].strip())
                        k += 1
                    if k < len(lines):
                        tail = lines[k]
                        before = tail.split(quote)[0].strip()
                        if before:
                            mlines.append(before)
                    for ml in mlines:
                        if ml:
                            doc_summary = ml
                            break
                    break
                elif l.startswith("return") or l.startswith("async") or l.startswith("@") or l.startswith("pass") or l.startswith("raise") or l.startswith("try"):
                    break
                elif l.strip() == "":
                    k += 1
                    continue
                else:
                    break

            results.append((decorator, func_name, signature, def_line_no, doc_summary))
            i = j + 1
        else:
            i += 1


    # print markdown table
    print("| Decorator | Function Name | Signature | Def line | Docstring summary |")
    print("|---|---|---|---:|---|")
    for dec, name, sig, lineno, doc in results:
        sig = sig.replace("|", "\\|")
        doc = doc.replace("|", "\\|")
        print(f"| {dec} | {name} | {sig} | {lineno} | {doc} |")
