# sdnext installer
import installer

dependencies = ['onnxruntime', 'pymatting', 'pooch']
for dependency in dependencies:
    if not installer.installed(dependency, quiet=True):
        installer.install(dependency, ignore=False)
