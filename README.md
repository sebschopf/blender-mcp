# blender-mcp

Petit projet d'intégration Blender ↔ MCP (Model Context Protocol).

But: centraliser les téléchargements, construire des matériaux/textures testables, et garder `addon.py` comme glue minimale pour Blender.

Structure principale
- `addon.py` : glue / point d'entrée Blender. Doit rester léger ; les opérations lourdes sont lazy-importées.
- `src/blender_mcp/` : package principal (helpers testables et code métier)
    - `downloaders.py` — téléchargements centralisés
    - `materials.py` — construction de spec de matériaux (pure) + wrapper Blender
    - `node_helpers.py` — petits helpers pour câbler les nodes (défensifs, testables)
    - `texture_helpers.py` — helpers pour charger/configurer images
    - `server.py` — serveur MCP / glue

Exécution des tests (terminal)
1. Active ton environnement Python (venv/conda) si nécessaire :

```powershell
.\.venv\Scripts\Activate.ps1
# ou conda activate <env>
```

2. Installer les dépendances de dev (si besoin) :

```powershell
python -m pip install -U pytest
```

3. Lancer les tests :

```powershell
#$ depuis la racine du repo
$env:PYTHONPATH = 'src'; python -m pytest -q
```

Note: Dans GitHub Actions la variable `PYTHONPATH` est définie comme `src:.` (séparateur `:` sur runners Linux) pour garantir que le répertoire racine du dépôt est également accessible pendant les tests. Localement, `PYTHONPATH='src'` (PowerShell : `$env:PYTHONPATH = 'src'`) suffit et correspond aux exemples fournis dans la documentation.

Configuration VS Code
- Un fichier `.vscode/settings.json` a été ajouté pour activer la découverte pytest dans l'IDE.
- Un `pytest.ini` est présent pour uniformiser la découverte des tests.

Notes d'implémentation
- Les helpers qui touchent `bpy` sont importés paresseusement (lazy import) pour éviter d'importer `bpy` lors d'une exécution hors-Blender.
- Les fonctions de `node_helpers` sont défensives : elles acceptent soit des objets réels de Blender, soit des containers mockables utilisés dans les tests.
- Pendant la refactorisation, j'ai préféré conserver des fallbacks inline dans `addon.py` pour garantir que l'addon continue de fonctionner directement dans Blender même si l'un des helpers échoue.

Que faire ensuite
- Continuer la délivrance : réduire encore `addon.py` pour qu'il fasse uniquement l'enregistrement et le lazy-import du serveur.
- Ajouter une petite CI GitHub Actions qui lance `pytest`, `ruff`, `mypy` sur les PRs.

Si tu veux que je pousse une branche ou crée un PR, dis-le et je prépare la branche + message de PR.

---
Fait par l'outil de refactorisation — instructions et notes en français pour usage local.



# BlenderMCP - Blender Model Context Protocol Integration

BlenderMCP connects Blender to Claude AI through the Model Context Protocol (MCP), allowing Claude to directly interact with and control Blender. This integration enables prompt assisted 3D modeling, scene creation, and manipulation.

**We have no official website. Any website you see online is unofficial and has no affiliation with this project. Use them at your own risk.**

[Full tutorial](https://www.youtube.com/watch?v=lCyQ717DuzQ)

### Join the Community

Give feedback, get inspired, and build on top of the MCP: [Discord](https://discord.gg/z5apgR8TFU)

### Supporters

[CodeRabbit](https://www.coderabbit.ai/)

[Satish Goda](https://github.com/satishgoda)

**All supporters:**

[Support this project](https://github.com/sponsors/ahujasid)

## Release notes (1.2.0)
- View screenshots for Blender viewport to better understand the scene
- Search and download Sketchfab models


### Previously added features:
- Support for Poly Haven assets through their API
- Support to generate 3D models using Hyper3D Rodin
- For newcomers, you can go straight to Installation. For existing users, see the points below
- Download the latest addon.py file and replace the older one, then add it to Blender
- Delete the MCP server from Claude and add it back again, and you should be good to go!

## Features

- **Two-way communication**: Connect Claude AI to Blender through a socket-based server
- **Object manipulation**: Create, modify, and delete 3D objects in Blender
- **Material control**: Apply and modify materials and colors
- **Scene inspection**: Get detailed information about the current Blender scene
- **Code execution**: Run arbitrary Python code in Blender from Claude

## Components

The system consists of two main components:

1. **Blender Addon (`addon.py`)**: A Blender addon that creates a socket server within Blender to receive and execute commands
2. **MCP Server (`src/blender_mcp/server.py`)**: A Python server that implements the Model Context Protocol and connects to the Blender addon

## Installation


### Prerequisites

- Blender 3.0 or newer
- Python 3.10 or newer
- uv package manager: 

**If you're on Mac, please install uv as**
```bash
brew install uv
```
**On Windows**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex" 
```
and then
```bash
set Path=C:\Users\nntra\.local\bin;%Path%
```

Otherwise installation instructions are on their website: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

**⚠️ Do not proceed before installing UV**

### Environment Variables

The following environment variables can be used to configure the Blender connection:

- `BLENDER_HOST`: Host address for Blender socket server (default: "localhost")
- `BLENDER_PORT`: Port number for Blender socket server (default: 9876)

Example:
```bash
export BLENDER_HOST='host.docker.internal'
export BLENDER_PORT=9876
```

### Claude for Desktop Integration

[Watch the setup instruction video](https://www.youtube.com/watch?v=neoK_WMq92g) (Assuming you have already installed uv)

Go to Claude > Settings > Developer > Edit Config > claude_desktop_config.json to include the following:

```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
```

### Cursor integration

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=blender&config=eyJjb21tYW5kIjoidXZ4IGJsZW5kZXItbWNwIn0%3D)

For Mac users, go to Settings > MCP and paste the following 

- To use as a global server, use "add new global MCP server" button and paste
- To use as a project specific server, create `.cursor/mcp.json` in the root of the project and paste


```json
{
    "mcpServers": {
        "blender": {
            "command": "uvx",
            "args": [
                "blender-mcp"
            ]
        }
    }
}
```

For Windows users, go to Settings > MCP > Add Server, add a new server with the following settings:

```json
{
    "mcpServers": {
        "blender": {
            "command": "cmd",
            "args": [
                "/c",
                "uvx",
                "blender-mcp"
            ]
        }
    }
}
```

[Cursor setup video](https://www.youtube.com/watch?v=wgWsJshecac)

**⚠️ Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both**

### Visual Studio Code Integration

_Prerequisites_: Make sure you have [Visual Studio Code](https://code.visualstudio.com/) installed before proceeding.

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_blender--mcp_server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22blender-mcp%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22blender-mcp%22%5D%7D)

### Installing the Blender Addon

1. Download the `addon.py` file from this repo
1. Open Blender
2. Go to Edit > Preferences > Add-ons
3. Click "Install..." and select the `addon.py` file
4. Enable the addon by checking the box next to "Interface: Blender MCP"


## Usage

### Starting the Connection
![BlenderMCP in the sidebar](assets/addon-instructions.png)

1. In Blender, go to the 3D View sidebar (press N if not visible)
2. Find the "BlenderMCP" tab
3. Turn on the Poly Haven checkbox if you want assets from their API (optional)
4. Click "Connect to Claude"
5. Make sure the MCP server is running in your terminal

If you prefer not to run a terminal each time, see `start-server.ps1` in the repository root — it will launch `blender-mcp` in a detached PowerShell process and write logs to `blender-mcp.log`.

Important note about the Add-on UI
----------------------------------
The Blender add-on UI no longer starts or stops the MCP server process directly. During the ongoing refactor we intentionally limited the add-on to a minimal, import-safe surface so it only toggles a UI flag (`blendermcp_server_running`) and informs users how to start/stop the server externally.

Recommended ways to run the MCP server:
- Use the provided PowerShell helper: `start-server.ps1` (Windows)
- Run the CLI entrypoint in a terminal: `blender-mcp` (after installing the package or using `poetry run`) 
- For HTTP/ASGI usage: run `uvicorn src.blender_mcp.asgi:app` (install `uvicorn[standard]` first)

This reduces accidental process management from within Blender and keeps the addon import-safe for CI and tests.

Alternatively you can expose an HTTP adapter (included as `src/blender_mcp/asgi.py`) and run it with uvicorn:

```powershell
# install the extras once
pip install "uvicorn[standard]" fastapi

# run the ASGI adapter (will start the MCP server in background)
uvicorn blender_mcp.asgi:app --host 127.0.0.1 --port 8000 --reload
```

Then use `http://127.0.0.1:8000/health` to verify the adapter and Blender connection.

### Using with Claude

Once the config file has been set on Claude, and the addon is running on Blender, you will see a hammer icon with tools for the Blender MCP.

![BlenderMCP in the sidebar](assets/hammer-icon.png)

#### Capabilities

- Get scene and object information 
- Create, delete and modify shapes
- Apply or create materials for objects
- Execute any Python code in Blender
- Download the right models, assets and HDRIs through [Poly Haven](https://polyhaven.com/)
- AI generated 3D models through [Hyper3D Rodin](https://hyper3d.ai/)


### Example Commands

Here are some examples of what you can ask Claude to do:

- "Create a low poly scene in a dungeon, with a dragon guarding a pot of gold" [Demo](https://www.youtube.com/watch?v=DqgKuLYUv00)
- "Create a beach vibe using HDRIs, textures, and models like rocks and vegetation from Poly Haven" [Demo](https://www.youtube.com/watch?v=I29rn92gkC4)
- Give a reference image, and create a Blender scene out of it [Demo](https://www.youtube.com/watch?v=FDRb03XPiRo)
- "Generate a 3D model of a garden gnome through Hyper3D"
- "Get information about the current scene, and make a threejs sketch from it" [Demo](https://www.youtube.com/watch?v=jxbNI5L7AH8)
- "Make this car red and metallic" 
- "Create a sphere and place it above the cube"
- "Make the lighting like a studio"
- "Point the camera at the scene, and make it isometric"

## Hyper3D integration

Hyper3D's free trial key allows you to generate a limited number of models per day. If the daily limit is reached, you can wait for the next day's reset or obtain your own key from hyper3d.ai and fal.ai.

## Troubleshooting

- **Connection issues**: Make sure the Blender addon server is running, and the MCP server is configured on Claude, DO NOT run the uvx command in the terminal. Sometimes, the first command won't go through but after that it starts working.
- **Timeout errors**: Try simplifying your requests or breaking them into smaller steps
- **Poly Haven integration**: Claude is sometimes erratic with its behaviour
- **Have you tried turning it off and on again?**: If you're still having connection errors, try restarting both Claude and the Blender server


## Technical Details

### Communication Protocol

The system uses a simple JSON-based protocol over TCP sockets:

- **Commands** are sent as JSON objects with a `type` and optional `params`
- **Responses** are JSON objects with a `status` and `result` or `message`

## Limitations & Security Considerations

### Legacy & Deprecation Plan

Ce projet est en phase de retrait progressif de plusieurs shims legacy (ex: `connection_core.py`, `simple_dispatcher.py`, façades `materials.py`, `blender_codegen.py`).

Ressources:
- Tracker détaillé: `docs/LEGACY_TRACKER.md`
- Spec calendrier (OpenSpec): `openspec/changes/2025-11-14-legacy-retirement-schedule/spec.md`
- Journal des étapes: `docs/PROJECT_JOURNAL.md`

Calendrier: retrait planifié N+2 (deux cycles après annonce) après audit et mise à jour du CHANGELOG. Pendant l'intervalle, les shims émettent un DeprecationWarning mais restent fonctionnels pour compatibilité.


- The `execute_blender_code` tool allows running arbitrary Python code in Blender, which can be powerful but potentially dangerous. Use with caution in production environments. ALWAYS save your work before using it.
- Poly Haven requires downloading models, textures, and HDRI images. If you do not want to use it, please turn it off in the checkbox in Blender. 
- Complex operations might need to be broken down into smaller steps


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Notes for contributors and maintainers (important)

- Optional google-genai integration: The project supports calling Gemini via the
    google-genai SDK, but this feature is intentionally optional. The import is
    guarded and the function `call_gemini_api` will raise a clear RuntimeError if
    the `google-genai` package is not installed. This keeps the core package
    usable in CI and by contributors who don't need this feature.

- Type stubs: We use `types-requests` in development to provide type hints for
    `requests`. Install dev dependencies (or at least `types-requests`) to get a
    clean `mypy` run locally.

- Lazy imports & casting: Modules that touch Blender (`bpy`) are imported
    lazily so the package can be imported outside Blender (for tests/CI). Some
    dynamic results returned by the Blender runtime are narrowed with
    `typing.cast(...)` to satisfy static typing while preserving runtime
    flexibility.

- If you're enabling the google-genai feature, set `GEMINI_API_KEY` and install
    `google-genai` in your environment. The README and `AUDIT.md` include a short
    checklist for safely enabling this feature.

## Disclaimer

This is a third-party integration and not made by Blender. Made by [Siddharth](https://x.com/sidahuj)
