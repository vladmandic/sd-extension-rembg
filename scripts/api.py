from fastapi import FastAPI, Body
import gradio as gr
from modules.api import api
from installer import installed

def rembg_api(_: gr.Blocks, app: FastAPI):
    @app.post("/rembg")
    async def rembg_remove(
        input_image: str = Body("", title='rembg input image'),
        model: str = Body("u2net", title='rembg model'),
        return_mask: bool = Body(False, title='return mask'),
        alpha_matting: bool = Body(False, title='alpha matting'),
        alpha_matting_foreground_threshold: int = Body(240, title='alpha matting foreground threshold'),
        alpha_matting_background_threshold: int = Body(10, title='alpha matting background threshold'),
        alpha_matting_erode_size: int = Body(10, title='alpha matting erode size'),
        refine: bool = Body(False, title="refine foreground (ben2 only)")
    ):
        try:
            import rembg
        except Exception:
            return
        if not model or model == "None":
            return

        input_image = api.decode_base64_to_image(input_image)

        if model == "ben2":
            try:
                import ben2
            except Exception:
                return
            image = ben2.remove(input_image, refine=refine)
        else:
            image = rembg.remove(
                input_image,
                session=rembg.new_session(model),
                only_mask=return_mask,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold,
                alpha_matting_erode_size=alpha_matting_erode_size,
            )
        return {"image": api.encode_pil_to_base64(image).decode("utf-8")}

try:
    if installed('rembg', reload=False, quiet=True):
        import modules.script_callbacks as script_callbacks
        script_callbacks.on_app_started(rembg_api)
except Exception:
    pass
