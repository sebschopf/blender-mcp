import ast
import os

root='src/blender_mcp'
threshold=80
results=[]
for dirpath,_,files in os.walk(root):
    for f in files:
        if f.endswith('.py'):
            path=os.path.join(dirpath,f)
            try:
                src=open(path,encoding='utf-8').read()
                tree=ast.parse(src)
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    start=node.lineno
                    end=getattr(node,'end_lineno',None)
                    if end is None:
                        # fallback: naive scan
                        end=start
                        lines=src.splitlines()
                        for i in range(start, min(start+2000, len(lines))):
                            end=i
                    length=end-start+1
                    if length>threshold:
                        kind='class' if isinstance(node,ast.ClassDef) else 'def'
                        name=node.name
                        results.append((length, kind, name, path, start, end))
results.sort(reverse=True)
for length,kind,name,path,start,end in results:
    print(f"{length:4} lines | {kind:5} | {name:30} | {path}:{start}-{end}")
