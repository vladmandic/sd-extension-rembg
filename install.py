# sdnext installer
import installer

dependencies = ['pymatting', 'pooch', 'rembg']
for dependency in dependencies:
    installer.install(dependency, ignore=False, quiet=True)
