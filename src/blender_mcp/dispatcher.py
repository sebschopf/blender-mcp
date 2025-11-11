"""Top-level re-export for the dispatcher package.

The real implementations live in `blender_mcp.dispatchers`. Keeping a
small re-export here allows existing imports (e.g. `import
blender_mcp.dispatcher`) to continue to work while the code is
reorganized.
"""

from .dispatchers.dispatcher import *  # noqa: F401,F403
# Explicitly re-export a few additional symbols expected by tests and
# callers that may not be present in the package __all__.
from .dispatchers.dispatcher import (
	HandlerError,
	HandlerNotFound,
	Handler,
	call_gemini_cli,
	call_mcp_tool,
	run_bridge,
	_CommandDispatcherCompat,
)

import importlib

# Provide a thin wrapper for run_bridge that ensures any monkeypatches made
# against the top-level `blender_mcp.dispatcher` module (tests often patch
# `dispatcher.call_gemini_cli`) are propagated into the relocated implementation
# before invocation. This keeps tests that patch the top-level module working.
_pkg = importlib.import_module("blender_mcp.dispatchers.dispatcher")

def run_bridge(user_req, config, dispatcher, use_api: bool = False):
	# copy the top-level callables into the implementation module so that
	# runtime monkeypatches are respected by the relocated run_bridge.
	_pkg.call_gemini_cli = call_gemini_cli
	_pkg.call_mcp_tool = call_mcp_tool
	return _pkg.run_bridge(user_req, config, dispatcher, use_api=use_api)


