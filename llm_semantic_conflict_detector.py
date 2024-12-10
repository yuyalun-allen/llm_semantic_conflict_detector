import os
import json
import requests


class MergeSenario():
    def __init__(self, repo_path: str, changed_file_dir: str, left_hash: str, right_hash: str, merge_hash: str) -> None:
        self.repo_path = repo_path
        self.changed_file_dir = changed_file_dir
        self.left_hash = left_hash
        self.right_hash = right_hash
        self.merge_hash = merge_hash
        self.left_changed_files = set()
        self.right_changed_files = set()

    def merge(self):
        pass

class TestGenerator():
    def __init__(self, llm_config: dict, merge_senario: MergeSenario) -> None:
        self.llm_config = llm_config
        self.merge_senario = merge_senario

    def generate_test_with_llm(self, file_path: str) -> str:
        response = ""
        with open(file_path) as f:
            file_content = f.read()
        prompt = \
f"""
You are an expert of writing unit tests. Please write a suite of unit tests with JUnit for the following Java code snippet.

{file_content}

You should write at least 3 test cases. Please make sure that the test cases are meaningful and cover the most important aspects of the code.
Write test code only. Make sure that the code compiles and runs without errors.
"""
        #TODO: this is for ollama
        response = requests.post(url=self.llm_config["url"] + "/api/generate",
                                 data=json.dumps({
                                    "model": self.llm_config["model_name"],
                                    "prompt": prompt,
                                    "stream": False
                                })).json()["response"]
        return response


    def generate(self):
        left_changed_file_path = ["/".join([self.merge_senario.changed_file_dir,
                                          self.merge_senario.merge_hash,
                                          self.merge_senario.left_hash,
                                          changed_file]) for changed_file in self.merge_senario.left_changed_files]
        right_changed_file_path = ["/".join([self.merge_senario.changed_file_dir,
                                          self.merge_senario.merge_hash,
                                          self.merge_senario.right_hash,
                                          changed_file]) for changed_file in self.merge_senario.right_changed_files]

        for path in left_changed_file_path + right_changed_file_path:
            test_content = self.generate_test_with_llm(path)
            # TODO: Supportted file type is only java
            with open(path.split(".")[0] + "Test.java") as f:
                f.write(test_content)

class TestRunner():
    def __init__(self, source_path: str, result_path: str) -> None:
        self.source_path = source_path
        self.report_path = result_path
        
    def run(self):
        pass

class TestAnalyzer():
    def __init__(self, result_path: str, report_path: str) -> None:
        self.result_path = result_path
        self.report_path = report_path

    def analyze(self):
        pass

class LLMSemanticConflictDetector():
    def __init__(self, llm_config: dict, merge_senario: MergeSenario) -> None:
        TEST_RESULT_PATH = "test_result"
        CONFLICT_REPORT_PATH = "conflict_report"
        os.makedirs(TEST_RESULT_PATH, exist_ok=True)
        os.makedirs(CONFLICT_REPORT_PATH, exist_ok=True)
        repo_name = merge_senario.repo_path.split("/")[-1]

        self.test_generator = TestGenerator(llm_config, merge_senario)
        self.test_runner = TestRunner(merge_senario.repo_path, f"{TEST_RESULT_PATH}/{repo_name}")
        self.test_analyzer = TestAnalyzer(f"{TEST_RESULT_PATH}/{repo_name}", f"{CONFLICT_REPORT_PATH}/{repo_name}")

    def run(self):
        self.test_generator.generate()
        self.test_runner.run()
        self.test_analyzer.analyze()
