import os
from src.data_loader.loader import DataLoader
from src.qa_engine.engine import QAEngine
from config.config import DATA_DIR, VECTOR_DB_PATH

def retrain():
    print("Retraining Bob with new data...")
    
    # Remove old index
    if os.path.exists(VECTOR_DB_PATH):
        os.remove(VECTOR_DB_PATH)
        print("Removed old knowledge base.")
    
    # Load all data
    loader = DataLoader(DATA_DIR)
    documents = loader.load_all_data()
    
    if not documents:
        print("No data files found!")
        return
    
    print(f"Found {len(documents)} documents.")
    
    # Build new index
    qa_engine = QAEngine()
    qa_engine.build_index(documents)
    
    print(f"✓ Knowledge base rebuilt with {len(documents)} documents!")
    print("Run 'python main.py' to start Bob.")

if __name__ == "__main__":
    retrain()
