import launch

if not launch.is_installed("rembg"):
    launch.run_pip("install rembg --no-deps", "rembg")

for dep in ['onnxruntime', 'pymatting', 'pooch']:
    if not launch.is_installed(dep):
        launch.run_pip(f"install {dep}", f"{dep}")
