from .utils import modify_function, process_logs, display_results
from .InternalTrackingState import InternalState
import time


class Tracker(InternalState):
    """
    Main Module class that tracks the execution time and results of a given function over multiple iterations.
    Parameters
    ----------
    function_object : callable
        The function to be tracked.
    namespace : dict, optional
        Additional namespace to provide to the function during execution, by default an empty dictionary.
    no_iterations : int, optional
        Number of iterations to run the tracked function, by default 3.
    Attributes
    ----------
    function_object : callable
        The tracked function.
    no_iterations : int
        Number of iterations to run the function.
    namespace : dict
        Namespace for the function's execution environment.
    executable_function : callable
        The executable version of the tracked function.
    Methods
    -------
    __call__(*param)
        Calls the tracked function with specified parameters and analyzes the results.
    get_executable()
        Generates an executable version of the tracked function.
    Examples
    --------
    To track the execution time and results of a function, you can use the `Tracker` class as shown below:
    >>> from codepulse import Tracker
    >>> def fun1(x, y):
    ...     m = 1
    ...     for i in range(x*100):
    ...         m = m * 3 
    ...         for j in range(x*30):
    ...             m = m + 4 
    ...     return m
    >>> t = Tracker(fun1)
    >>> t(3, 5)
    This will execute the `fun1` function with the specified parameters and analyze the results over multiple iterations.
    The tracked function's execution times and analysis results will be displayed in a formatted table.
    """

    def __init__(self, function_object, namespace={}, no_iterations=3):
        self.function_object = function_object
        self.no_iterations = no_iterations
        self.namespace = {"time": time}
        self.namespace.update(namespace)

        super().__init__(modify_function(self.function_object))
        self.executable_function = self.get_executable()

    def __call__(self, *param, **params):
        items = []
        total_time = []
        for i in range(self.no_iterations):
            t1 = time.time()
            _ = self.executable_function(*param, **params)
            t2 = time.time()
            total_time.append((t2 - t1) * 1000)
            items.append(_[-1])
        self[1] = process_logs(items)
        display_results(
            self[1], total_time, self.no_iterations, self.function_object.__name__
        )

    def get_executable(self):
        namespace = self.namespace.copy()
        exec(self[0], namespace)
        return namespace[self.function_object.__name__]