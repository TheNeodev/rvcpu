import gradio as gr
import os
import numpy as np
from pydub import AudioSegment
from rvc import VoiceClone
import argparse
import shutil
parser = argparse.ArgumentParser()
parser.add_argument('--share', action='store_true', help='Share the Gradio app', default=False)
args = parser.parse_args()
vc = None
weight_root = 'assets/weights'
index_root =  'logs'
#model_files = [f for f in os.listdir(weight_root) if f.endswith('.pth')] if os.path.exists(weight_root) and os.listdir(weight_root) else []
index_files = []
for root, dirs, files in os.walk(index_root):
    for file in files:
        if file.endswith('.index'):
            index_files.append(os.path.join(root, file))

model_files = []
for root, dirs, files in os.walk(weight_root):
    for file in files:
        if file.endswith('.pth'):
            index_files.append(os.path.join(root, file))



def initialize_vc(model, index):
    global vc
    if model in model_files:
        vc = VoiceClone(model, os.path.basename(index))
        print(f"Model Loaded: {model}")
        return True
    else:
        gr.Warning(f"Invalid model selection: {model}. Please choose a valid model.")
        return None

# Find the .index under the folder that shares a name with the selected .pth model
def find_matching_index(model_path):
    try:
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        for index_file in index_files:
            if model_name in index_file:
                return index_file
    except:
        pass

def convert_audio(audio_path, use_chunks, chunk_size, f0up_key, f0method, index_rate, protect, model_dropdown, index_dropdown):
    print(audio_path, use_chunks, chunk_size, f0up_key, f0method, index_rate, protect, model_dropdown, index_dropdown)
    global vc
    if vc == None:
        try:
            model_name, index_name = model_dropdown, index_dropdown
            initialize_vc(model_name, index_name)
            print("Model initialized.")
        except Exception as e:
            gr.Warning("Please select a model and index file.")
            print(e)
            return None
    vc.f0up_key = f0up_key
    vc.f0method = f0method
    vc.index_rate = index_rate
    vc.protect = protect
    if use_chunks:
        rate, data = vc.convert_chunks(audio_path, chunk_size=chunk_size)
    else:
        rate, data = vc.convert(audio_path)
    return (rate, np.array(data))



with gr.Blocks(title="🔊",theme=gr.themes.Base()) as app:
    gr.Markdown("# 📱VoiceCloner")
    with gr.Row():
        gr.HTML("<a href='https://ko-fi.com/rejekts' target='_blank'>🤝 Donate </a>")
    with gr.Row():
        with gr.Column():
            model_dropdown = gr.Textbox(label=" pth path")        
            index_dropdown = gr.Textbox(label=" index path")
            
            audio_input = gr.Textbox(label="Input Audio")
            with gr.Accordion("Settings",open=False):
                use_chunks = gr.Checkbox(label="Use Chunks", value=True)
                chunk_size = gr.Slider(1, 30, value=10, step=1, label="Chunk Size (seconds)")
                f0up_key = gr.Slider(-12, 12, value=0, step=1, label="Pitch Shift")
                f0method = gr.Dropdown(["pm", "rmvpe"], value="pm", label="F0 Method")
                index_rate = gr.Slider(0, 1, value=0.66, step=0.01, label="Index Rate")
                protect = gr.Slider(0, 0.5, value=0.33, step=0.01, label="Protect")
            convert_btn = gr.Button("Convert")
            audio_output = gr.Audio(label="Converted Audio",interactive=False)
            
    convert_btn.click(
        convert_audio,
        inputs=[audio_input, use_chunks, chunk_size, f0up_key, f0method, index_rate, protect, model_dropdown, index_dropdown],
        outputs=[audio_output]
    )
    



app.launch(share=args.share,allowed_paths=["a.png","kofi_button.png"])
