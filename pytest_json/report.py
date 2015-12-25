# -*- coding: utf-8 -*-

import os
import sys
import time
import json


# python 2 open doesn't support encoding
PY3 = sys.version_info[0] == 3
if not PY3:
    from codecs import open


class JSONReport(object):
    def __init__(self, json_path):
        self.json_path = os.path.abspath(
            os.path.expanduser(os.path.expandvars(json_path)))
        self.reports = []
        self.errors = 0
        self.failed = 0
        self.passed = 0
        self.skipped = 0
        self.xfailed = 0
        self.xpassed = 0

    def pytest_runtest_logreport(self, report):
        if not (report.skipped or report.failed or report.passed):
            return

        report_dict = {
            'nodeid': report.nodeid,
            'duration': '{0:.2f}'.format(getattr(report, 'duration', 0.0)),
            'outcome': report.outcome,
            'stage': report.when
        }

        if report.longrepr:
            report_dict['longrepr'] = str(report.longrepr)

        for header, content in report.sections:
            report_dict[header] = content

        self.reports.append(report_dict)

    def pytest_sessionstart(self, session):
        self.session_start_time = time.time()

    def pytest_sessionfinish(self, session):
        session_stop_time = time.time()
        session_duration = session_stop_time - self.session_start_time

        env = {}
        if session.config._json_environment:
            for key, value in session.config._json_environment:
                env[key] = value

        report = {
            'duration': '{0:.2f}'.format(session_duration),
            'environment': env,
            'tests': self.reports,
            'num_tests': len(self.reports)
        }

        if not os.path.exists(os.path.dirname(self.json_path)):
            os.makedirs(os.path.dirname(self.json_path))

        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep('-', 'generated json report: {0}'.format(
            self.json_path))
