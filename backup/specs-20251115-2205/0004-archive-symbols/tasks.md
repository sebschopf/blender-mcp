# 0004 Tasks

1. Review archived files and ensure the `symbols/` directory contains one file per exported symbol with disposition and test references.
2. Add compatibility tests for `addon.register`/`unregister` and for `BlenderMCPServer` wrapper.
3. If a symbol is to be ported, create a follow-up OpenSpec change under `openspec/changes/<next-id>/` referencing this symbol.
4. Run `openspec validate --strict` on the `0004` change and fix any format issues.
