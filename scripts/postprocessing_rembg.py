import os
import gradio as gr
from modules import scripts_postprocessing
from modules.paths import models_path
from modules import shared


models = [
    "None",
    "silueta",
    "u2net",
    "u2net_human_seg",
    "isnet-general-use",
    "isnet-anime",
    # "u2netp",
    # "u2net_cloth_seg",
    # "sam",
]


def dependencies():
    import installer
    for pkg in ['pymatting', 'pooch', 'rembg']:
        if not installer.installed(pkg):
            installer.install(pkg, ignore=False)


class ScriptPostprocessingUpscale(scripts_postprocessing.ScriptPostprocessing):
    name = "Remove background"
    order = 20000
    model = None

    def ui(self):
        with gr.Accordion('Remove background', open = False):
            with gr.Row():
                model = gr.Dropdown(label="Model", choices=models, value="None", elem_id="extras_rembg_model")
                only_mask = gr.Checkbox(label="Return mask", value=False, elem_id="extras_rembg_only_mask")
                postprocess_mask = gr.Checkbox(label="Postprocess mask", value=False, elem_id="extras_rembg_process_mask")
                alpha_matting = gr.Checkbox(label="Alpha matting", value=True, elem_id="extras_rembg_alpha")
            with gr.Row(visible=True) as alpha_mask_row:
                alpha_matting_erode_size = gr.Slider(label="Erode size", minimum=0, maximum=40, step=1, value=10, elem_id="extras_rembg_alpha_erode")
                alpha_matting_foreground_threshold = gr.Slider(label="Foreground threshold", minimum=0, maximum=255, step=1, value=240, elem_id="extras_rembg_alpha_foreground")
                alpha_matting_background_threshold = gr.Slider(label="Background threshold", minimum=0, maximum=255, step=1, value=10, elem_id="extras_rembg_alpha_background")
            alpha_matting.change(fn=lambda x: gr.update(visible=x), inputs=[alpha_matting], outputs=[alpha_mask_row])
            return {
                "model": model,
                "only_mask": only_mask,
                "postprocess_mask": postprocess_mask,
                "alpha_matting": alpha_matting,
                "alpha_matting_foreground_threshold": alpha_matting_foreground_threshold,
                "alpha_matting_background_threshold": alpha_matting_background_threshold,
                "alpha_matting_erode_size": alpha_matting_erode_size,
            }

    def process(self, pp: scripts_postprocessing.PostprocessedImage, model, only_mask, postprocess_mask, alpha_matting, alpha_matting_foreground_threshold, alpha_matting_background_threshold, alpha_matting_erode_size): # pylint: disable=arguments-differ
        dependencies()
        try:
            import rembg
        except Exception as e:
            shared.log.error(f'Rembg load failed: {e}')
            return
        if not model or model == "None":
            return
        if "U2NET_HOME" not in os.environ:
            os.environ["U2NET_HOME"] = os.path.join(models_path, "Rembg")
        args = {
            'data': pp.image,
            'only_mask': only_mask,
            'post_process_mask': postprocess_mask,
            'bgcolor': None,
            'alpha_matting': alpha_matting,
            'alpha_matting_foreground_threshold': alpha_matting_foreground_threshold,
            'alpha_matting_background_threshold': alpha_matting_background_threshold,
            'alpha_matting_erode_size': alpha_matting_erode_size,
            'session': rembg.new_session(model),
        }
        """
        # sam is more of a segment-anything model as it needs set of labels an points
        if model == 'sam':
            import numpy as np
            args['input_points'] = np.array([[400, 350], [700, 400], [200, 400]]) # array of y,x
            args['input_labels'] = np.array([1, 1, 2])
        """
        pp.image = rembg.remove(**args)
        pp.info["Rembg"] = model
