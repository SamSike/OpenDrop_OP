import pytest
import os


def run_all_pytest():
    root_dir = os.path.dirname(os.path.abspath(__file__))

    test_dirs = [
        os.path.join(root_dir, "opendrop-ml/modules"),
        os.path.join(root_dir, "opendrop-ml/views"),
    ]

    args = [
        "-v",
        "--tb=short",
        "--maxfail=3",
        "--disable-warnings",
    ]

    args += test_dirs

    return pytest.main(args)


if __name__ == "__main__":
    raise SystemExit(run_all_pytest())
