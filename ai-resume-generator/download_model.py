#!/usr/bin/env python3
"""
Pre-download the sentence transformer model to avoid hanging during first import
"""

import os
import sys
from pathlib import Path

def download_model():
    print("🔄 Pre-downloading sentence transformer model...")
    print("This will download ~80MB and may take a few minutes...")
    
    try:
        # Set cache directory
        cache_dir = Path.home() / ".cache" / "huggingface"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Cache directory: {cache_dir}")
        
        # Set environment variables for faster downloads
        os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '0'  # Show progress
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'     # Disable telemetry
        
        print("📦 Importing sentence_transformers...")
        import time
        start_time = time.time()
        
        from sentence_transformers import SentenceTransformer
        
        import_time = time.time() - start_time
        print(f"✅ Import completed in {import_time:.1f} seconds")
        
        print("⬇️ Loading all-MiniLM-L6-v2 model...")
        download_start = time.time()
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        download_time = time.time() - download_start
        print(f"✅ Model loaded in {download_time:.1f} seconds")
        
        # Test the model
        print("🧪 Testing model...")
        test_sentence = ["This is a test sentence for the model."]
        embeddings = model.encode(test_sentence)
        
        total_time = time.time() - start_time
        print(f"✅ Model downloaded and tested successfully!")
        print(f"📊 Embedding shape: {embeddings.shape}")
        print(f"⏱️ Total time: {total_time:.1f} seconds")
        print("🎉 Future imports will be much faster!")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("💡 You can still use the system without semantic similarity features")
        return False

if __name__ == "__main__":
    print("🤖 AI Resume Generator - Model Setup")
    print("=" * 50)
    
    success = download_model()
    
    if success:
        print("\n✅ Setup complete! You can now run:")
        print("   python run_tests.py")
        print("   uvicorn app.main:app --reload")
    else:
        print("\n⚠️ Model download failed, but you can still continue.")
        print("The system will work without semantic similarity features.")
        
    sys.exit(0 if success else 1)
