from llm_semantic_conflict_detector import LLMSemanticConflictDetector, MergeSenario

if __name__ == "__main__":
    llm_config = {
            "url": "http://127.0.0.1:11434", 
            "model_name": "gemma"
            }
    merge_senario = MergeSenario(repo_path="", merge_hash="", left_hash="", right_hash="", changed_file_dir="merge_files")
    LLMSemanticConflictDetector(llm_config, merge_senario).run()
