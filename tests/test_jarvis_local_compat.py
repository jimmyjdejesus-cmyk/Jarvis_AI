# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/




Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

import importlib
import warnings
import sys
import pytest

def test_jarvis_local_import_emits_deprecation():
    # Ensure we can import the shim
    if "Jarvis_Local" in sys.modules:
        del sys.modules["Jarvis_Local"]
        
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always", DeprecationWarning)
        import Jarvis_Local
        
        # Check for the specific warning message
        found_warning = False
        for w in rec:
            if issubclass(w.category, DeprecationWarning) and "`Jarvis_Local` moved to `apps.Jarvis_Local`" in str(w.message):
                found_warning = True
                break
                
        assert found_warning, "Importing Jarvis_Local should emit DeprecationWarning"
        
        # Basic sanity: ensure the module resolves to the apps package underneath
        # Note: The shim might replace sys.modules entry, so we check if it behaves like the new module
        assert hasattr(Jarvis_Local, "__file__") or hasattr(Jarvis_Local, "__path__")

def test_apps_jarvis_local_import():
    import apps.Jarvis_Local
    assert apps.Jarvis_Local is not None
