import os
import gradio as gr
from modules import scripts_postprocessing
from modules.paths import models_path
from modules.ui_components import FormRow


ok = True
try:
    import rembg
except Exception as e:
    print(f'Rembg load failed: {e}')
    ok = False


models = [
    "None",
    "silueta",
    "u2net",
    # "u2netp",
    "u2net_human_seg",
    # "u2net_cloth_seg",
    "isnet-general-use",
    "isnet-anime",
    # "sam",
]

class ScriptPostprocessingUpscale(scripts_postprocessing.ScriptPostprocessing):
    name = "Rembg"
    order = 20000
    model = None

    def ui(self):
        if not ok:
            return {}
        with FormRow():
            model = gr.Dropdown(label="Model", choices=models, value="None")
            only_mask = gr.Checkbox(label="Return mask", value=False)
            postprocess_mask = gr.Checkbox(label="Postprocess mask", value=False)
            alpha_matting = gr.Checkbox(label="Alpha matting", value=True)
        with FormRow(visible=True) as alpha_mask_row:
            alpha_matting_erode_size = gr.Slider(label="Erode size", minimum=0, maximum=40, step=1, value=10)
            alpha_matting_foreground_threshold = gr.Slider(label="Foreground threshold", minimum=0, maximum=255, step=1, value=240)
            alpha_matting_background_threshold = gr.Slider(label="Background threshold", minimum=0, maximum=255, step=1, value=10)
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
        if not model or model == "None" or not ok:
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
