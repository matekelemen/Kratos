import KratosMultiphysics as KM
from KratosMultiphysics import Testing
from KratosMultiphysics.kratos_utilities import GetNotAvailableApplications

from unittest import * # needed to make all functions available to the tests using this file
from unittest.util import safe_repr
from contextlib import contextmanager

import argparse
import sys
import os
import time


class TestLoader(TestLoader):
    def loadTestsFromTestCases(self, testCaseClasses):
        ''' Return a list of suites with all tests cases contained in every
        testCaseClass in testCaseClasses '''

        allTests = []

        for caseClasses in testCaseClasses:
            caseTests = self.loadTestsFromTestCase(caseClasses)
            allTests.append(caseTests)

        return allTests


test_timing_results = {}

class TestCase(TestCase):

    def run(self, result=None):
        start_time = time.time()
        super().run(result)
        time_needed = time.time()-start_time
        test_timing_results[time_needed] = str(self)

    def skipTestIfApplicationsNotAvailable(self, *application_names):
        '''Skips the test if required applications are not available'''
        required_but_not_available_apps = GetNotAvailableApplications(*application_names)
        if len(required_but_not_available_apps) > 0:
            self.skipTest('Required Applications are missing: "{}"'.format('", "'.join(required_but_not_available_apps)))

    def assertEqualTolerance(self, first, second, tolerance, msg=None):
        ''' Fails if first and second have a difference greater than
        tolerance '''

        if first < (second - tolerance) or first > (second + tolerance):
            raise self.failureException(msg or '%r != %r within %r places' % (first, second, tolerance))

    def assertIsClose(self, first, second, rel_tol=None, abs_tol=None, msg=None):
        ''' Fails if the two objects are unequal as determined by their
        absolute and relative difference

        If the two objects compare equal then they will automatically
        compare relative almost equal. '''

        if first == second:
            # shortcut
            return

        if rel_tol is None:
            rel_tol = 1e-09
        if abs_tol is None:
            abs_tol = 0.0

        if isclose(first, second, rel_tol, abs_tol):
            return

        standardMsg = '%s != %s within %s rel-tol and %s abs-tol' % (safe_repr(first),
                                                     safe_repr(second),
                                                     rel_tol, abs_tol)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

    def assertVectorAlmostEqual(self, vector1, vector2, places=7, msg=None, delta=None):
        class LazyErrMsg:
            '''Since potentially expensive, this class delays printing the error message until it is actually needed'''
            def __init__(self, mismatch_idx, aux_message=None):
                self.mismatch_idx = mismatch_idx
                self.aux_message=aux_message

            def __str__(self):
                err_msg  = '\nCheck failed because vector arguments are not equal in component {}'.format(self.mismatch_idx)
                err_msg += '\nVector 1:\n{}\nVector 2:\n{}'.format(vector1, vector2)
                if self.aux_message:
                    err_msg += "\n{}".format(self.aux_message)
                return err_msg

        self.assertEqual(len(vector1), len(vector2), msg="\nCheck failed because vector arguments do not have the same size")
        for i, (v1, v2) in enumerate(zip(vector1, vector2)):
            self.assertAlmostEqual(v1, v2, places = places, msg = LazyErrMsg(i, msg), delta = delta)

    def assertMatrixAlmostEqual(self, matrix1, matrix2, places=7, msg=None, delta=None):
        class LazyDimErrMsg:
            '''Since potentially expensive, this class delays printing the error message until it is actually needed'''
            def __init__(self, aux_message=None):
                self.aux_message = aux_message

            def __str__(self):
                err_msg  = '\nCheck failed because matrix arguments do not have the same dimensions:\n'
                err_msg += 'First argument has dimensions ({},{}), '.format(matrix1.Size1(), matrix1.Size2())
                err_msg += 'Second argument has dimensions ({},{})'.format(matrix2.Size1(), matrix2.Size2())
                if self.aux_message:
                    err_msg += "\n{}".format(self.aux_message)
                return err_msg

        class LazyValErrMsg:
            '''Since potentially expensive, this class delays printing the error message until it is actually needed'''
            def __init__(self, idx_1, idx_2, aux_message=None):
                self.idx_1 = idx_1
                self.idx_2 = idx_2
                self.aux_message = aux_message

            def __str__(self):
                err_msg  = '\nCheck failed because matrix arguments are not equal in component ({},{})'.format(self.idx_1, self.idx_2)
                err_msg += '\nMatrix 1:\n{}\nMatrix 2:\n{}'.format(matrix1, matrix2)
                if self.aux_message:
                    err_msg += "\n{}".format(self.aux_message)
                return err_msg

        dimensions_match = (matrix1.Size1() == matrix2.Size1() and matrix1.Size2() == matrix2.Size2())
        self.assertTrue(dimensions_match, msg=LazyDimErrMsg(msg))

        for i in range(matrix1.Size1()):
            for j in range(matrix1.Size2()):
                self.assertAlmostEqual(matrix1[i,j], matrix2[i,j], places, LazyValErrMsg(i,j,msg), delta)

class KratosTextTestResult(TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream=stream, descriptions=descriptions,
                         verbosity=verbosity)
        self.buffer = True
        self.__start_time = None
        self.show_test_times = verbosity > 1

    def startTest(self, test):
        super().startTest(test)
        self.__start_time = time.perf_counter()

    def addError(self, test, err):
        self.__stop_time = time.perf_counter()-self.__start_time
        if self.show_test_times:
            self.stream.write("{0:>4.3f}s ...".format(self.__stop_time))
        super().addError(test, err)

    def addExpectedFailure(self, test, err):
        self.__stop_time = time.perf_counter()-self.__start_time
        if self.show_test_times:
            self.stream.write("{0:>4.3f}s ...".format(self.__stop_time))
        super().addExpectedFailure(test, err)

    def addFailure(self, test, err):
        self.__stop_time = time.perf_counter()-self.__start_time
        if self.show_test_times:
            self.stream.write("{0:>4.3f}s ...".format(self.__stop_time))
        super().addFailure(test, err)

    def addSkip(self, test, reason):
        self.__stop_time = time.perf_counter()-self.__start_time
        if self.show_test_times:
            self.stream.write("{0:>4.3f}s ...".format(self.__stop_time))
        super().addSkip(test, reason)

    def addSuccess(self, test):
        self.__stop_time = time.perf_counter()-self.__start_time
        if self.show_test_times:
            self.stream.write("{0:>4.3f}s ...".format(self.__stop_time))
        super().addSuccess(test)

    def addUnexpectedSuccess(self, test):
        self.__stop_time = time.perf_counter()-self.__start_time
        if self.show_test_times:
            self.stream.write("{0:>4.3f}s ...".format(self.__stop_time))
        super().addUnexpectedSuccess(test)

    def getDescription(slef, test):
        return str(test)

def skipIfApplicationsNotAvailable(*application_names):
    '''Skips the test if required applications are not available'''
    required_but_not_available_apps = GetNotAvailableApplications(*application_names)
    reason_for_skip = 'Required Applications are missing: "{}"'.format('", "'.join(required_but_not_available_apps))
    return skipIf(len(required_but_not_available_apps) > 0, reason_for_skip)


@contextmanager
def SupressConsoleOutput():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

@contextmanager
def SupressConsoleError():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

@contextmanager
def SupressAllConsole():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        old_stdout = sys.stdout
        sys.stderr = devnull
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr
            sys.stdout = old_stdout

def main():
    # this deliberately overiddes the function "unittest.main",
    # because it cannot parse extra command line arguments
    if "--using-mpi" in sys.argv:
        sys.argv.remove("--using-mpi") # has to be removed bcs unittest cannot parse it
    import unittest
    unittest.main()

def runTests(tests):
    # parse command line options
    parser = argparse.ArgumentParser()

    # Depending of serial/MPI the level can be different, so we have to parse it
    if KM.IsDistributedRun():
        parser.add_argument('-l', '--level', default='mpi_small',
            choices=['mpi_all', 'mpi_nightly', 'mpi_small', 'mpi_validation', 'all', 'nightly', 'small', 'validation'],
            help="For distributed runs, options that don't start with mpi_ will be replaced by the corresponding mpi version")
    else:
        parser.add_argument('-l', '--level', default='small', choices=['all', 'nightly', 'small', 'validation'])
    parser.add_argument('-v', '--verbosity', default=2, type=int, choices=[0, 1, 2])
    parser.add_argument('--timing', action='store_true')
    parser.add_argument('--using-mpi', action='store_true')

    args = parser.parse_args()

    level = args.level
    if args.using_mpi:
        if not "mpi_" in level:
            level = "mpi_" + level

    if tests[level].countTestCases() == 0:
        print('[Warning]: "{}" test suite is empty'.format(level),file=sys.stderr)
    else:
        result = not TextTestRunner(verbosity=args.verbosity, buffer=True, resultclass=KratosTextTestResult).run(tests[level]).wasSuccessful()
        if Testing.GetDefaultDataCommunicator().Rank() == 0 and args.timing:
            print("Test Execution Times:")
            for test_time, test_name in sorted(test_timing_results.items(), reverse=True):
                print(test_name, " {0:.{1}f} [sec]".format(test_time,2))
        sys.exit(result)


KratosSuites = {
    'small':          TestSuite(),
    'nightly':        TestSuite(),
    'all':            TestSuite(),
    'validation':     TestSuite(),
    'mpi_small':      TestSuite(),
    'mpi_nightly':    TestSuite(),
    'mpi_all':        TestSuite(),
    'mpi_validation': TestSuite(),
}


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    ''' Same implementation as math.isclose
    self-implemented bcs math.isclose was only introduced in python3.5
    see https://www.python.org/dev/peps/pep-0485/ '''
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class WorkFolderScope:
    """ Helper-class to execute test in a specific target path
        Input
        -----
        - rel_path_work_folder: String
            Relative path of the target dir from the calling script

        - file_path: String
            Absolute path of the calling script

        - add_to_path: Bool
            "False" (default) if no need to add the target dir to the path, "True" otherwise.
    """

    def __init__(self, rel_path_work_folder, file_path, add_to_path=False):
        self.currentPath = os.getcwd()
        self.add_to_path = add_to_path
        if self.add_to_path:
            self.currentPythonpath = sys.path
        self.scope = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(file_path)), rel_path_work_folder))

    def __enter__(self):
        os.chdir(self.scope)
        if self.add_to_path:
            sys.path.append(self.scope)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.currentPath)
        if self.add_to_path:
            sys.path.remove(self.scope)
