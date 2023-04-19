"""
This module defines a singleton object, "patchmatch" that
wraps the actual patchmatch object. It respects the global
"try_patchmatch" attribute, so that patchmatch loading can
be suppressed or deferred
"""
import numpy as np

from invokeai.backend.globals import Globals


class PatchMatch:
    """
    Thin class wrapper around the patchmatch function.
    """

    patch_match = None
    tried_load: bool = False

    def __init__(self):
        super().__init__()

    @classmethod
    def _load_patch_match(cls):
        if cls.tried_load:
            return
        if Globals.try_patchmatch:
            from patchmatch import patch_match as pm

            if pm.patchmatch_available:
                print(">> Patchmatch initialized")
            else:
                print(">> Patchmatch not loaded (nonfatal)")
            cls.patch_match = pm
        else:
            print(">> Patchmatch loading disabled")
        cls.tried_load = True

    @classmethod
    def patchmatch_available(cls) -> bool:
        cls._load_patch_match()
        return cls.patch_match and cls.patch_match.patchmatch_available

    @classmethod
    def inpaint(cls, *args, **kwargs) -> np.ndarray:
        if cls.patchmatch_available():
            return cls.patch_match.inpaint(*args, **kwargs)
