
import pytest

import gitgo

@pytest.mark.placeholder
class TestSetup:
    def test_frontend(self):
        fe = gitgo.frontend.Frontend(backend=gitgo.backend.null.NullBackend())
