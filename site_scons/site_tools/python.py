import os
import subprocess


def exists(env):
    return env.Detect('python3') or env.Detect('python')


def generate(env):
    python = env.Detect('python3') or env.Detect('python') or os.environ.get('PYTHON', None)
    env.SetDefault(PYTHON=python)

    if env['PYTHON'] is None:
        print("Could not find python executable")
        env.Exit(1)


    env['PYTHONVERSION'] = \
        subprocess.check_output([
            env.subst('$PYTHON'),
            '-c',
            "import sys; print('%d.%d.%d' % sys.version_info[:3])"
        ]) \
        .decode() \
        .strip()

    env['PYTHON_DISTUTILS_PLATFORM'] = \
        subprocess.check_output([
            env.subst('$PYTHON'),
            '-c',
            "import distutils.util; print(distutils.util.get_platform())"
        ]) \
        .decode() \
        .strip()

    env['PYTHONINCLUDES'] = env.Dir(
        subprocess.check_output([
            env.subst('$PYTHON'),
            '-c',
            "import sysconfig; print(sysconfig.get_path('include'))"
        ])
        .decode()
        .strip()
    )

    env['PYTHON_EXT_SUFFIX'] = \
        subprocess.check_output([
            env.subst('$PYTHON'),
            '-c',
            "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
        ]) \
        .decode() \
        .strip()

    paths = \
        subprocess.check_output([
            env.subst('$PYTHON'),
            '-c',
            "import sys; print('\\n'.join(sys.path))"
        ]) \
        .decode() \
        .strip() \
        .split('\n')
    
    env['PYTHONPATH'] = env.Dir([p for p in paths if os.path.isdir(p)])
