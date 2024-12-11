import os
import re
import json
import requests


class MergeScenario():
    def __init__(self, repo_path: str, changed_file_dir: str, left_hash: str, right_hash: str, merge_hash: str) -> None:
        self.repo_path = repo_path
        self.changed_file_dir = changed_file_dir
        self.left_hash = left_hash
        self.right_hash = right_hash
        self.merge_hash = merge_hash
        self.left_changed_files = {"DeploymentEntityManager.java"}
        self.right_changed_files = {"DeploymentEntityManager.java"}

    def merge(self):
        pass

    def get_left_dir(self) -> str:
        return "/".join([self.changed_file_dir, self.merge_hash, self.left_hash])

    def get_right_dir(self) -> str:
        return "/".join([self.changed_file_dir, self.merge_hash, self.right_hash])

class TestGenerator():
    def __init__(self, llm_config: dict, merge_scenario: MergeScenario) -> None:
        self.llm_config = llm_config
        self.merge_scenario = merge_scenario

    def generate_test_with_llm(self, file_path: str) -> str:
        with open(file_path) as f:
            file_content = f.read()
        prompt = \
f"""
You are an expert of writing unit tests. Please write a suite of unit tests with JUnit for the following Java code snippet.

{file_content}

Surround the test code with "```java```" tag.
You should write at least 3 test cases.
Please make sure that the test cases are meaningful and cover the most important aspects of the code.
Make sure that the code compiles and runs without errors.
"""
        #TODO: this is for ollama
        response = requests.post(url=self.llm_config["url"] + "/api/generate",
                                 data=json.dumps({
                                    "model": self.llm_config["model_name"],
                                    "prompt": prompt,
                                    "stream": False
                                })).json()["response"]
        test_code = re.findall(r"```java(.*?)```", response, re.DOTALL)[0]
        return test_code


    def generate(self):
        left_dir = self.merge_scenario.get_left_dir()
        right_dir = self.merge_scenario.get_right_dir()
        left_changed_file_path = [f"{left_dir}/{changed_file}" 
                                                for changed_file in self.merge_scenario.left_changed_files]
        right_changed_file_path = [f"{right_dir}/{changed_file}"
                                                for changed_file in self.merge_scenario.right_changed_files]

        for path in left_changed_file_path + right_changed_file_path:
            test_content = self.generate_test_with_llm(path)
            # TODO: Supportted file type is only java
            with open(path.split(".")[0] + "Test.java", "w") as f:
                f.write(test_content)

    def fix_compilation_error(self):
        pass

    def fix_runtime_error(self):
        pass

class TestRunner():
    def __init__(self, merge_scenario: MergeScenario, result_path: str) -> None:
        self.merge_scenario = merge_scenario
        self.result_path = result_path
        
    def run(self):
        left_dir = self.merge_scenario.get_left_dir()
        right_dir = self.merge_scenario.get_right_dir()
        left_test_file_path = [f"{left_dir}/{changed_file.split(".")[0] + "Test.java"}"
                                            for changed_file in self.merge_scenario.left_changed_files]
        right_test_file_path = [f"{right_dir}/{changed_file.split(".")[0] + "Test.java"}"
                                            for changed_file in self.merge_scenario.right_changed_files]
        # TODO: make the path configurable
        JUNIT_JAR_PATH = "/home/allen/.local/share/maven/repository/junit/junit/4.13.2/*"
        MOCKITO_JAR_PATH = "/home/allen/.local/share/maven/repository/org/mockito/mockito-core/5.5.0/*"
        left_test_path = f"{left_dir}/test_class"
        left_classpath = f"{JUNIT_JAR_PATH}:{MOCKITO_JAR_PATH}:{left_dir}/target/*"
        right_test_path = f"{right_dir}/test_class"
        right_classpath = f"{JUNIT_JAR_PATH}:{MOCKITO_JAR_PATH}:{right_dir}/target/*"

        for left_test in left_test_file_path:
            os.system(f"javac -cp {left_classpath} {left_test} -d {left_test_path}")
            os.system(f"java -cp {right_classpath}:{left_test_path} org.junit.platform.console.ConsoleLauncher --select-class {left_test.split('/')[-1]}Test")

        for right_test in right_test_file_path:
            os.system(f"javac -cp {right_classpath} {right_test} -d {right_test_path}")
            os.system(f"java -cp {left_classpath}:{right_test_path} org.junit.platform.console.ConsoleLauncher --select-class {right_test.split('/')[-1]}Test")
    
    def compile(self) -> bool:
        pass

    def correctness_test(self) -> bool:
        pass

    # TODO: drop flaky test
    def test(self):
        pass

class TestAnalyzer():
    def __init__(self, result_path: str, report_path: str) -> None:
        self.result_path = result_path
        self.report_path = report_path

    def analyze(self):
        pass

class LLMSemanticConflictDetector():
    def __init__(self, llm_config: dict, merge_scenario: MergeScenario) -> None:
        TEST_RESULT_PATH = "test_result"
        CONFLICT_REPORT_PATH = "conflict_report"
        os.makedirs(TEST_RESULT_PATH, exist_ok=True)
        os.makedirs(CONFLICT_REPORT_PATH, exist_ok=True)
        repo_name = merge_scenario.repo_path.split("/")[-1]

        self.test_generator = TestGenerator(llm_config, merge_scenario)
        self.test_runner = TestRunner(merge_scenario, f"{TEST_RESULT_PATH}/{repo_name}")
        self.test_analyzer = TestAnalyzer(f"{TEST_RESULT_PATH}/{repo_name}", f"{CONFLICT_REPORT_PATH}/{repo_name}")

    def run(self):
        MAX_RETRY = 10
        self.test_generator.generate()

        while(self.test_runner.compile() != True):
            if MAX_RETRY == 0:
                raise Exception("Compilation error is not fixed after 10 retries")
            MAX_RETRY -= 1
            self.test_generator.fix_compilation_error()

        while(self.test_runner.correctness_test() != True):
            if MAX_RETRY == 0:
                raise Exception("Runtime error is not fixed after 10 retries")
            MAX_RETRY -= 1
            self.test_generator.fix_runtime_error()
        
        self.test_runner.test()
        self.test_analyzer.analyze()
