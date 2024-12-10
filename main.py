from llm_semantic_conflict_detector import LLMSemanticConflictDetector, MergeSenario
import re

if __name__ == "__main__":
    llm_config = {
            "url": "http://127.0.0.1:11434", 
            "model_name": "llama3.2"
            }
    merge_senario = MergeSenario(repo_path="", merge_hash="merge", left_hash="left", right_hash="right", changed_file_dir="merge_files")
    LLMSemanticConflictDetector(llm_config, merge_senario).run()
