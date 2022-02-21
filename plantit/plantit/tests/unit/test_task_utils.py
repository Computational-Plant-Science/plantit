import uuid
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from plantit.tasks.models import Task
from plantit.utils.tasks import parse_task_walltime, has_output_target, get_output_included_patterns, get_output_included_names, parse_task_eta, \
    parse_task_time_limit, parse_task_miappe_info


class TaskUtilsTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='wbonelli', first_name="Wes", last_name="Bonelli")

    def test_parse_task_walltime_throws_value_error_when_malformed(self):
        with self.assertRaises(ValueError):
            parse_task_walltime('10:00')

        with self.assertRaises(ValueError):
            parse_task_walltime('10:00:02.04')

        with self.assertRaises(ValueError):
            parse_task_walltime('1')

        with self.assertRaises(ValueError):
            parse_task_walltime('not even close')

    def test_parse_task_walltime_when_valid(self):
        walltime = parse_task_walltime('10:09:08')
        total_seconds = (10 * 60 * 60) + (9 * 60) + 8
        self.assertEqual(walltime.total_seconds(), total_seconds)

        walltime = parse_task_walltime('10:9:8')
        total_seconds = (10 * 60 * 60) + (9 * 60) + 8
        self.assertEqual(walltime.total_seconds(), total_seconds)

    def test_has_output_target_when_does(self):
        user = User.objects.get(username='wbonelli')
        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            name=guid,
            user=user,
            workflow={
                'output': {
                    'to': '/iplant/home/wbonelli/some_folder'
                }
            }
        )

        self.assertTrue(has_output_target(task))

    def test_has_output_target_when_doesnt(self):
        user = User.objects.get(username='wbonelli')

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            name=guid,
            user=user,
            workflow={
                'output': None
            }
        )

        self.assertFalse(has_output_target(task))

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            name=guid,
            user=user,
            workflow={}
        )

        self.assertFalse(has_output_target(task))

    def test_get_output_included_patterns(self):
        user = User.objects.get(username='wbonelli')

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            job_id=guid,
            name=guid,
            user=user,
            workflow={
                'output': None
            }
        )

        # even if no output config is provided, we still want default inclusions
        expected = sorted(['zip'])
        actual = sorted(get_output_included_patterns(task))
        self.assertEqual(actual, expected)

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            name=guid,
            user=user,
            workflow={
                'output': {
                    'include': {
                        'patterns': []
                    }
                }
            }
        )

        actual = sorted(get_output_included_patterns(task))
        self.assertEqual(actual, expected)

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            name=guid,
            user=user,
            workflow={
                'output': {
                    'include': {
                        'patterns': [
                            'txt',
                            'png'
                        ]
                    }
                }
            }
        )

        patterns = sorted(get_output_included_patterns(task))
        for pattern in expected: self.assertIn(pattern, patterns)
        self.assertIn('txt', patterns)
        self.assertIn('png', patterns)

    def test_get_output_included_names(self):
        user = User.objects.get(username='wbonelli')

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            job_id=guid[0:7],
            name=guid,
            user=user,
            workflow={
                'output': None
            }
        )

        # even if no output config is provided, we still want default inclusions
        expected = sorted([
            # f"{guid}.zip",
            # f"plantit.{guid[0:7]}.out",
            # f"plantit.{guid[0:7]}.err",
        ])
        actual = sorted(get_output_included_names(task))
        self.assertEqual(actual, expected)

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            job_id=guid[0:7],
            name=guid,
            user=user,
            workflow={
                'output': {
                    'include': {
                        'names': []
                    }
                }
            }
        )

        expected = sorted([
            # f"{guid}.zip",
            # f"plantit.{guid[0:7]}.out",
            # f"plantit.{guid[0:7]}.err",
        ])
        actual = sorted(get_output_included_names(task))
        self.assertEqual(actual, expected)

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            job_id=guid[0:7],
            name=guid,
            user=user,
            workflow={
                'output': {
                    'include': {
                        'names': [
                            'file1.txt',
                            'file2.png'
                        ]
                    }
                }
            }
        )

        names = get_output_included_names(task)
        self.assertIn('file1.txt', names)
        self.assertIn('file2.png', names)
        # self.assertIn(f"{guid}.zip", names)
        # self.assertIn(f"plantit.{guid[0:7]}.out", names)
        # self.assertIn(f"plantit.{guid[0:7]}.err", names)

    def test_parse_task_eta(self):
        user = User.objects.get(username='wbonelli')

        guid = str(uuid.uuid4())
        task = Task.objects.create(
            guid=guid,
            job_id=guid[0:7],
            name=guid,
            user=user,
            workflow={
                'output': None
            }
        )

    def test_parse_task_eta_when_complete(self):
        delay = {'delay': 10, 'units': 'seconds'}
        eta, seconds = parse_task_eta(delay)
        self.assertTrue(eta > timezone.now())  # TODO: how to precisely test this?
        self.assertEqual(seconds, 10)

        delay = {'delay': 10, 'units': 'minutes'}
        eta, seconds = parse_task_eta(delay)
        self.assertTrue(eta > timezone.now())  # TODO: how to precisely test this?
        self.assertEqual(seconds, 10 * 60)

        delay = {'delay': 10, 'units': 'hours'}
        eta, seconds = parse_task_eta(delay)
        self.assertTrue(eta > timezone.now())  # TODO: how to precisely test this?
        self.assertEqual(seconds, 10 * 60 * 60)

        delay = {'delay': 10, 'units': 'days'}
        eta, seconds = parse_task_eta(delay)
        self.assertTrue(eta > timezone.now())  # TODO: how to precisely test this?
        self.assertEqual(seconds, 10 * 60 * 60 * 24)

    def test_parse_task_eta_when_missing_units(self):
        delay = {'delay': 10}
        eta, seconds = parse_task_eta(delay)
        self.assertTrue(eta > timezone.now())
        self.assertEqual(seconds, 10)

    def test_parse_task_eta_when_missing_delay(self):
        delay = {'units': 'seconds'}
        with self.assertRaises(ValueError):
            eta, seconds = parse_task_eta(delay)

    def test_parse_task_time_limit_when_complete(self):
        delay = {'limit': 10, 'units': 'seconds'}
        seconds = parse_task_time_limit(delay)
        self.assertEqual(seconds, 10)

        delay = {'limit': 10, 'units': 'minutes'}
        seconds = parse_task_time_limit(delay)
        self.assertEqual(seconds, 10 * 60)

        delay = {'limit': 10, 'units': 'hours'}
        seconds = parse_task_time_limit(delay)
        self.assertEqual(seconds, 10 * 60 * 60)

        delay = {'limit': 10, 'units': 'days'}
        seconds = parse_task_time_limit(delay)
        self.assertEqual(seconds, 10 * 60 * 60 * 24)

    def test_parse_task_time_limit_when_missing_units(self):
        delay = {'limit': 10}
        seconds = parse_task_time_limit(delay)
        self.assertEqual(seconds, 10)

    def test_parse_task_time_limit_when_missing_value(self):
        delay = {'units': 'seconds'}
        with self.assertRaises(ValueError):
            seconds = parse_task_time_limit(delay)

    def test_parse_task_miappe_info_when_neither_project_nor_study(self):
        miappe = {}
        project, study = parse_task_miappe_info(miappe)
        self.assertIsNone(project)
        self.assertIsNone(study)

    def test_parse_task_miappe_info_when_project_but_no_study(self):
        miappe = {'project': 'test-project'}
        project, study = parse_task_miappe_info(miappe)
        self.assertEqual(project, 'test-project')
        self.assertIsNone(study)

    def test_parse_task_miappe_info_when_project_and_study(self):
        miappe = {'project': 'test-project', 'study': 'test-study'}
        project, study = parse_task_miappe_info(miappe)
        self.assertEqual(project, 'test-project')
        self.assertEqual(study, 'test-study')
