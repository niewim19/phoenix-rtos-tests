import logging

from .builder import TargetBuilder
from .config import YAMLParser
from .device import RunnerFactory
from .testcase import TestCaseFactory


class TestsRunner:
    """Class responsible for loading, building and running tests"""

    def __init__(self, targets, test_paths, build=True):
        self.targets = targets
        self.test_configs = []
        self.test_paths = test_paths
        self.tests_per_target = {k: [] for k in targets}
        self.build = build
        self.runners = {target: RunnerFactory.create(target) for target in self.targets}
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def search_for_tests(self):
        paths = []
        for path in self.test_paths:
            candidate = list(path.rglob('test*.yaml'))
            if not candidate:
                raise ValueError(f'Test {path} does not contain .yaml test configuration')
            paths.extend(candidate)

        self.test_paths = paths

    def parse_tests(self):
        self.test_configs = []
        for path in self.test_paths:
            parser = YAMLParser(path, self.targets)
            testcase_config = parser.parse_test_config()
            self.test_configs.extend(testcase_config)
            logging.debug(f"File {path} parsed successfuly\n")

    def run(self):
        self.search_for_tests()
        self.parse_tests()

        for test_config in self.test_configs:
            test = TestCaseFactory.create(test_config)
            self.tests_per_target[test.target].append(test)

        if self.build:
            for target in self.targets:
                TargetBuilder(target).build()

        for runner in self.runners.values():
            runner.flash()

        for target, tests in self.tests_per_target.items():
            for test_case in tests:
                test_case.log_test_started()
                self.runners[target].run(test_case)
                test_case.log_test_status()

        for target, tests in self.tests_per_target.items():
            # Convert bools to int
            for test in tests:
                self.passed += int(test.passed())
                self.failed += int(test.failed())
                self.skipped += int(test.skipped())

        return self.passed, self.failed, self.skipped
