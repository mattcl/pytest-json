# -*- coding: utf-8 -*-

import datetime
import json
import os
import re
import sys
import time


# python 2 open doesn't support encoding
PY3 = sys.version_info[0] == 3
if not PY3:
    from codecs import open


class JSONReport(object):
    def __init__(self, json_path):
        self.json_path = os.path.abspath(
            os.path.expanduser(os.path.expandvars(json_path)))
        self.reports = {}
        self.summary = {}

    def _get_outcome(self, report):
        if report.failed:
            if report.when != 'call':
                return 'error'
            else:
                if hasattr(report, 'wasxfail'):
                    return 'xpassed'
                else:
                    return 'failed'
        elif report.skipped:
            if hasattr(report, 'wasxfail'):
                return 'xfailed'
            else:
                return 'skipped'

        return report.outcome

    def _update_summary(self, outcome, report):
        if report.passed and report.when != 'call':
            # do not count successful setup and teardown
            return

        if outcome not in self.summary:
            self.summary[outcome] = 1
        else:
            self.summary[outcome] += 1

    def pytest_runtest_logreport(self, report):
        outcome = self._get_outcome(report)

        self._update_summary(outcome, report)

        stage_dict = {
            'name': report.when,
            'duration': getattr(report, 'duration', 0.0),
            'outcome': outcome
        }

        if hasattr(report, 'metadata'):
            stage_dict['metadata'] = report.metadata

        if hasattr(report, 'wasxfail'):
            stage_dict['xfail_reason'] = report.wasxfail

        if report.longrepr:
            stage_dict['longrepr'] = str(report.longrepr)

        # only show stdout/stderr for the current stage
        stage_matcher = re.compile(r'^Captured.*{}$'.format(report.when))
        for header, content in report.sections:
            if stage_matcher.match(header):
                stage_dict[header] = content

        if report.nodeid not in self.reports:
            self.reports[report.nodeid] = {
                'name': report.nodeid,
                'duration': stage_dict['duration']
            }

        self.reports[report.nodeid][report.when] = stage_dict
        self.reports[report.nodeid]['duration'] += stage_dict['duration']

    def pytest_sessionstart(self, session):
        self.session_start_time = time.time()

    def _get_overall_outcome(self, report):
        if report['setup']['outcome'] != 'passed':
            return report['setup']['outcome']

        # if the call has passed, just return the outcome of teardown (which
        # might be an error)
        if report['call']['outcome'] == 'passed':
            return report['teardown']['outcome']

        return report['call']['outcome']

    def pytest_sessionfinish(self, session):
        session_stop_time = time.time()
        session_duration = session_stop_time - self.session_start_time

        env = {}
        if session.config._json_environment:
            for key, value in session.config._json_environment:
                env[key] = value

        created = datetime.datetime.now()
        created.strftime('%d-%b-%Y %H:%M:%S')

        self.summary['num_tests'] = len(self.reports)
        self.summary['duration'] = session_duration

        # format the reports
        tests = []
        for test, report in self.reports.items():
            report['outcome'] = self._get_overall_outcome(report)
            tests.append(report)

        report = {
            'environment': env,
            'tests': tests,
            'summary': self.summary,
            'created_at': str(created)
        }

        if not os.path.exists(os.path.dirname(self.json_path)):
            os.makedirs(os.path.dirname(self.json_path))

        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep('-', 'generated json report: {0}'.format(
            self.json_path))
