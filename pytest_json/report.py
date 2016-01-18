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
    def __init__(self, json_path, jsonapi):
        self.json_path = os.path.abspath(
            os.path.expanduser(os.path.expandvars(json_path)))
        self.jsonapi = jsonapi
        self.nodes = {}
        self.summary = {}
        self.run_index = 0
        self.report = {}

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

    def _make_stage_dict(self, report):
        outcome = self._get_outcome(report)

        stage_dict = {
            'name': report.when,
            'duration': getattr(report, 'duration', 0.0),
            'outcome': outcome
        }

        if hasattr(report, 'stage_metadata'):
            stage_dict['metadata'] = report.stage_metadata

        if hasattr(report, 'wasxfail'):
            stage_dict['xfail_reason'] = report.wasxfail

        if report.longrepr:
            stage_dict['longrepr'] = str(report.longrepr)

        # only show stdout/stderr for the current stage
        stage_matcher = re.compile(r'^Captured (.+) {}$'.format(report.when))
        for header, content in report.sections:
            match = stage_matcher.match(header)
            if match:
                stage_dict[match.group(1)] = content

        return stage_dict

    def pytest_runtest_logreport(self, report):
        stage_dict = self._make_stage_dict(report)

        self._update_summary(stage_dict['outcome'], report)

        if hasattr(report, 'report_metadata'):
            if 'metadata' not in self.report:
                self.report['metadata'] = []

            self.report['metadata'].append(report.report_metadata)

        if report.nodeid not in self.nodes:
            self.nodes[report.nodeid] = {
                'name': report.nodeid,
                'duration': stage_dict['duration'],
                'run_index': self.run_index
            }
            self.run_index += 1

        self.nodes[report.nodeid][report.when] = stage_dict
        self.nodes[report.nodeid]['duration'] += stage_dict['duration']

        # do this after we know we've created the nodeid in reports
        if hasattr(report, 'test_metadata'):
            if 'metadata' not in self.nodes[report.nodeid]:
                self.nodes[report.nodeid]['metadata'] = []

            self.nodes[report.nodeid]['metadata'].append(
                report.test_metadata)


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

    def _default_report(self, env, tests, created_at):
        report = {
            'report': {
                'environment': env,
                'tests': tests,
                'summary': self.summary,
                'created_at': created_at
            }
        }

        if 'metadata' in self.report:
            report['report']['metadata'] = self.report['metadata']

        return report

    def _jsonapi(self, env, tests, created_at):
        test_index = 1
        normalized_tests = []
        for test in tests:
            normalized_tests.append({
                'id': test_index,
                'type': 'test',
                'attributes': test
            })
            test_index += 1

        report = {
            'data': [
                {
                    'type': 'report',
                    'id': 1,  # this is arbitrary for now
                    'attributes': {
                        'environment': env,
                        'summary': self.summary,
                        'created_at': created_at
                    },
                    'relationships': {
                        'tests': {
                            'data': [
                                {'id': test['id'], 'type': 'test'} for test in normalized_tests
                            ]
                        }
                    }
                }
            ],
            'included': normalized_tests
        }

        if 'metadata' in self.report:
            report['data']['attributes']['metadata'] = self.report['metadata']

        return report

    def pytest_sessionfinish(self, session):
        session_stop_time = time.time()
        session_duration = session_stop_time - self.session_start_time

        env = {}
        if session.config._json_environment:
            for key, value in session.config._json_environment:
                env[key] = value

        created = datetime.datetime.now()
        created_at = str(created)

        self.summary['num_tests'] = len(self.nodes)
        self.summary['duration'] = session_duration

        # format the reports
        tests = []
        for test, report in self.nodes.items():
            report['outcome'] = self._get_overall_outcome(report)
            tests.append(report)

        if self.jsonapi:
            report = self._jsonapi(env, tests, created_at)
        else:
            report = self._default_report(env, tests, created_at)

        if not os.path.exists(os.path.dirname(self.json_path)):
            os.makedirs(os.path.dirname(self.json_path))

        with open(self.json_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(report))

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep('-', 'generated json report: {0}'.format(
            self.json_path))
