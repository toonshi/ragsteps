import os
from transformers import DPRQuestionEncoder, DPRQuestionEncoderTokenizer
from transformers.utils import WEIGHTS_NAME, CONFIG_NAME
import requests
from tqdm import tqdm
import streamlit as st

MODEL_NAME = "facebook/dpr-question_encoder-single-nq-base"
MODEL_FILES = [WEIGHTS_NAME, CONFIG_NAME, 'tokenizer_config.json', 'vocab.txt', 'tokenizer.json']
CACHE_DIR = os.path.join(os.path.dirname(__file__), "model_cache", MODEL_NAME.split('/')[-1])

def download_with_progress(url, filename):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    # Create a progress bar
    progress_text = f"Downloading {filename}"
    progress_bar = st.progress(0, text=progress_text)
    
    # Download with progress updates
    block_size = 1024
    downloaded = 0
    
    with open(filename, 'wb') as f:
        for data in response.iter_content(block_size):
            downloaded += len(data)
            f.write(data)
            # Update progress bar
            if total_size:
                progress = int(100 * downloaded / total_size)
                progress_bar.progress(progress/100, text=f"{progress_text}: {progress}%")
    
    # Complete the progress bar
    progress_bar.progress(1.0, text=f"{filename} downloaded!")
    return filename

def setup_model_with_progress():
    """Download and set up DPR model with progress tracking"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Check if model is already downloaded
    all_files_exist = all(
        os.path.exists(os.path.join(CACHE_DIR, f))
        for f in MODEL_FILES
    )
    
    if all_files_exist:
        st.success("✅ Model files already downloaded!")
    else:
        st.warning("⏳ Downloading model files (this will take a few minutes)...")
        
        # Download each model file
        for filename in MODEL_FILES:
            file_url = f"https://huggingface.co/{MODEL_NAME}/resolve/main/{filename}"
            target_path = os.path.join(CACHE_DIR, filename)
            
            if not os.path.exists(target_path):
                download_with_progress(file_url, target_path)
    
    # Load models from cache
    st.info("Loading models into memory...")
    question_encoder = DPRQuestionEncoder.from_pretrained(CACHE_DIR)
    question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained(CACHE_DIR)
    
    return question_encoder, question_tokenizer