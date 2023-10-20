import importlib.metadata
import packaging.requirements


def test_pip_check_for_all_extras():
    """We use a [default] extra to simplify extracting the [test] extra
    into a separate requirements file, but extras are not covered by `pip check`
    """
    # Adapted from pypa/pip#4824
    requirements = [
        packaging.requirements.Requirement(x) for x in
        importlib.metadata.metadata('vivi.core').get_all('Requires-Dist')]
    for req in requirements:
        installed = importlib.metadata.distribution(req.name)
        assert req.specifier.contains(installed.version, prereleases=True)
