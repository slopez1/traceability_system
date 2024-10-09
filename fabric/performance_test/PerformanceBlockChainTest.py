import asyncio
import time
import numpy as np

class PerformanceBlockChainTest:

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    def latency(self, func, validator, *args, **kwargs):
        """
        Evaluates the latency of the function `func` in seconds and checks the validity of the result using `validator`.

        Parameters:
        - func: the function whose latency you want to measure.
        - validator: a function that wait until confirm transaction is present.
        - *args: positional arguments to pass to `func`.
        - **kwargs: keyword arguments to pass to `func`.

        Returns:
        - total_time: the latency of the function in seconds.
        """
        start_time = time.time()  # Mark the time before execution
        self.loop.run_until_complete(func(*args, **kwargs))  # Execute the function
        validator(self.loop, *args, **kwargs)
        end_time = time.time()  # Mark the time after execution
        total_time = end_time - start_time  # Calculate latency
        return total_time

    def throughput_serial(self, func, validator, generator, max_time, wait_time_until_validation):
        """
        Evaluates the throughput of a system.

        Parameters:
        - func: The function to be executed repeatedly.
        - validator: a function that validate the correctness of transaction on the end.
        - generator: Generate te correct args for func for .
        - max_time: Maximum time allowed for executing the function (in seconds).

        Returns:
        - throughput: The total number of successful validations (True) after all executions.
        """
        # Execute the function with each set of inputs from func_inputs
        start_time = time.time()  # Registrar el tiempo de inicio
        count = 0
        used_args = []

        # Bucle que ejecuta la función hasta que se agote el tiempo
        print("Init Throughput_serial " + str(time.time()))
        while (time.time() - start_time) < max_time:
            args = next(generator)
            used_args.append(args)
            self.loop.run_until_complete(func(*args))  # Ejecutar la función con los argumentos proporcionados
            count += 1  # Incrementar el contador de ejecuciones
        print("Wait to validate throughput " + str(time.time()))
        time.sleep(wait_time_until_validation)
        print("End Wait to validate throughput " + str(time.time()))
        correct_count = 0
        for args in used_args:
            correct_count += validator(self.loop, *args)
        print("Validated to validate throughput  " + str(time.time()))
        return count, correct_count



    def response_time(self, func, *args, **kwargs):
        """
        Evaluates the response_time of the function `func` in seconds.

        Parameters:
        - func: the function whose latency you want to measure.
        - *args: positional arguments to pass to `func`.
        - **kwargs: keyword arguments to pass to `func`.

        Returns:
        - total_time: the response time of the function in seconds.
        """
        start_time = time.time()  # Mark the time before execution
        self.loop.run_until_complete(func(*args, **kwargs))  # Execute the function
        end_time = time.time()  # Mark the time after execution
        total_time = end_time - start_time  # Calculate latency
        return total_time

    def test_function_return(self, func, *args, **kwargs):
        return self.loop.run_until_complete(func(*args, **kwargs))

    def time_statistics(self, times):
        """
        Calculates latency statistics from an array of times.

        Parameters:
        - times: An array/list of time values (latencies)

        Returns:
        - A dictionary with the following metrics:
            - average: Average latency
            - median: Median latency (P50)
            - max: Maximum latency
            - min: Minimum latency
            - standard_deviation: Standard deviation of latencies
            - percentiles: A dictionary with P50, P90, P99, and P99.9
        """
        # Convert the list to a numpy array for easier calculations
        times = np.array(times)

        # Calculate basic statistics
        average = str(np.mean(times))
        median = str(np.median(times))
        max_latency = str(np.max(times))
        min_latency = str(np.min(times))
        standard_deviation = str(np.std(times))

        # Calculate common percentiles
        percentiles = {
            "P50": str(np.percentile(times, 50)),
            "P90": str(np.percentile(times, 90)),
            "P99": str(np.percentile(times, 99)),
            "P99.9": str(np.percentile(times, 99.9))
        }

        # Return a dictionary with the results
        return {
            "average": average,
            "median": median,
            "max": max_latency,
            "min": min_latency,
            "standard_deviation": standard_deviation,
            "percentiles": percentiles
        }







