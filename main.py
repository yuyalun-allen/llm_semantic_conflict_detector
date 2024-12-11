from llm_semantic_conflict_detector import LLMSemanticConflictDetector, MergeScenario

if __name__ == "__main__":
    llm_config = {
            "url": "http://127.0.0.1:11434", 
            "model_name": "qwen2.5-coder:7b"
            }
    CHANGED_FILE_PATH = "changed_files"
    merge_scenario = MergeScenario(repo_path="", merge_hash="merge", left_hash="left", right_hash="right", changed_file_dir=CHANGED_FILE_PATH)
    LLMSemanticConflictDetector(llm_config, merge_scenario).run()
