import inspect
import pandas as pd


def modify_function(function_object):
    """
    Modify a given function by adding time tracking statements after each line.

    Parameters
    ----------
    function_object : callable
        The function to be modified.

    Returns
    -------
    str
        A modified string representation of the input function with added time tracking statements.

    Notes
    -----
    This function takes the source code of the input function, inserts time tracking statements after each line,
    and returns the modified string representation of the function.

    """
    # add timer for each line
    source_code = inspect.getsource(function_object)
    source_code = source_code.split("\n")
    prefix = source_code[0]  # def func1():

    variables = ["time.perf_counter()"]
    variables1 = []
    body = source_code[1:]
    modified_body = []
    trackers = []
    initial_indent = None
    prev_indent = None
    skip_indent = None
    consumed = None # prevents getting one indentation being empty completely

    # clean body
    temp_body = []
    for i, b in enumerate(body):
        l_strip = b.lstrip()
        indent = len(b) - len(b.lstrip())
        if prev_indent is None:
            prev_indent = indent

        if l_strip == "" or any(l_strip.startswith(p) for p in ["#"]):
            # don't include intentation value or anything from here completely ignore
            continue
        if initial_indent is None:
            # any execution coming here means it is not # or just empty line. It can be print
            initial_indent = indent
        if indent > prev_indent:
            # entering for loop 
            consumed = False
        if any(l_strip.startswith(p) for p in ["print("]):
            # don't include intentation value or anything from here completely ignore
            if prev_indent > indent and not consumed:
                # so case where for loop had only print statements
                temp_body += [f"{' '*prev_indent}#placeholder"]
            prev_indent = indent
            continue
        if prev_indent is not None and prev_indent > indent:
            # we came out of the loop: this puts placeholder after the last line in inner for/while etc loop
            temp_body += [f"{' '*prev_indent}#placeholder"]
        prev_indent = indent
        temp_body += [b]
        consumed = True
    if prev_indent is not None and initial_indent is not None and initial_indent != prev_indent:
        temp_body += [f"{' '*initial_indent}#placeholder"]

    body = temp_body.copy()
    prev_indent = None
    for i, b in enumerate(body):
        l_strip = b.lstrip()
        indent = len(b) - len(b.lstrip())
        if any(l_strip.startswith(p) for p in ["elif", "else"]):
            # we add these lines but no tracker on it.
            # Doesn't matter what we put we remove it on placeholder
            # we do 0 if variables[-1] is None which takes care
            trackers.append(f"({i}, '''{' '*indent}{l_strip}''', {0})")
            modified_body += [" " * indent + l_strip]
            continue
        if initial_indent is None:
            initial_indent = indent
            prev_indent = indent

        # take care of special case
        if skip_indent is not None and skip_indent == indent:
            # this is a below return and at same indent so continue
            continue
        elif skip_indent is not None and skip_indent != indent:
            # previously it was in skip not now
            skip_indent = None

        s = f"{' '*indent}time_watcher_{i} = time.perf_counter()"
        s1 = f"{' '*indent}max_watcher_{i} = max(max_watcher_{i}, 0.0 if {variables[-1]} is None else time_watcher_{i} - {variables[-1]})"

        variables.append(f"time_watcher_{i}")
        variables1.append(f"max_watcher_{i}")

        if l_strip.startswith("return "):
            # it is a return
            skip_indent = indent
            trackers.append(
                f"({i}, '''{' '*indent}{l_strip}''', time_watcher_{i}, max_watcher_{i})"
            )
            b1 = " " * indent + l_strip + ", ( " + ", ".join(trackers) + ")"
            modified_body += [s, s1, b1]
            continue
        trackers.append(
            f"({i}, '''{' '*indent}{l_strip}''', time_watcher_{i}, max_watcher_{i})"
        )
        modified_body += [s, s1, " " * indent + l_strip]

    if initial_indent is None:
        initial_indent = 0
    # we will not enter here if function has return call, if not then we enter here
    pre_suffix = f"{' '*initial_indent}time_watcher_{i+1} = time.perf_counter()"
    s1 = f"{' '*initial_indent}max_watcher_{i+1} = max(max_watcher_{i+1}, 0.0 if {variables[-1]} is None else time_watcher_{i+1} - {variables[-1]})"  # {0 if variables[-1] is 'None' else f'time_watcher_{i+1} - {variables[-1]}'})"
    variables.append(f"time_watcher_{i+1}")
    variables1.append(f"max_watcher_{i+1}")

    trackers.append(
        f"({i+1}, '''{' '*indent}end_tracker''', time_watcher_{i+1}, max_watcher_{i+1})"
    )
    modified_body += [pre_suffix, s1, f"""{' '*initial_indent}end_tracker = 6"""]

    # we should have initial indent by now
    default_values = [" " * initial_indent + k + " = None" for k in variables[1:]]
    default_values1 = [" " * initial_indent + k + " = 0.0" for k in variables1]
    modified_function = (
        [prefix]
        + default_values
        + default_values1
        + modified_body
        + [" " * initial_indent + "return 1" + ", ( " + ", ".join(trackers) + ")"]
    )

    return "\n".join(modified_function)


def merge_text(x):
    """
    Merge non-empty text values from an iterable into a single string.

    Parameters
    ----------
    x : iterable
        Iterable containing text values.

    Returns
    -------
    str
        A single string formed by merging the non-empty text values from the iterable.

    Raises
    ------
    Exception
        If all text values in the iterable are empty.

    Notes
    -----
    This function iterates through the provided iterable and merges the non-empty text values into a single string.
    If all text values are empty, an Exception is raised.

    """
    for i in x:
        if str(i).rstrip() != "":
            return str(i).rstrip()
    raise Exception()


def find_valid_line(df):
    """
    Combine text from columns in a DataFrame to form valid lines, filling NaN values with empty strings.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing text data.

    Returns
    -------
    numpy.ndarray
        An array of strings, where each row represents a valid line created from the non-NaN values in the columns.

    Notes
    -----
    This function takes a DataFrame with text data and combines the non-NaN values from relevant columns to form
    valid lines. The resulting array can be used to display formatted text output.

    """
    line_cols = [i for i in df.columns if i.startswith("line_")]
    x = df[line_cols]
    out = x.fillna("").apply(lambda x: merge_text(x), axis=1).values
    return out


def mean_excluding_nan_count(x):
    """
    Calculate the mean of a pandas Series while excluding NaN values.

    Parameters
    ----------
    x : pandas.Series
        A pandas Series containing numerical values, possibly including NaNs.

    Returns
    -------
    float
        The calculated mean of the provided Series, excluding NaN values.

    Notes
    -----
    This function calculates the mean of the provided pandas Series, excluding any NaN values present in the Series.

    """
    x = x.dropna()
    return x.mean()


def std_excluding_nan_count(x):
    """
    Calculate the standard deviation of a pandas Series while excluding NaN values.

    Parameters
    ----------
    x : pandas.Series
        A pandas Series containing numerical values, possibly including NaNs.

    Returns
    -------
    float
        The calculated standard deviation of the provided Series, excluding NaN values.

    Notes
    -----
    This function calculates the standard deviation of the provided pandas Series, excluding any NaN values present in the Series.

    """
    x = x.dropna()
    return x.std()


def process_logs(items):
    """
    Process tracked logs and calculate mean and standard deviation of execution times for each line.

    Parameters
    ----------
    items : list of tuples
        List of tuples containing tracked data for each iteration.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the calculated mean and standard deviation of execution times for each line.

    Notes
    -----
    This function takes a list of tracked data for each iteration and calculates the mean and standard deviation of
    execution times for each line across the iterations. The returned DataFrame provides insights into the execution
    performance of different lines within the tracked function.

    """
    df1 = pd.DataFrame()
    for i, item in enumerate(items):
        if df1.empty == True:
            df = pd.DataFrame(item)
            df.columns = [
                "LineNo",
                f"line_{i}",
                f"time_watcher_{i}",
                f"max_watcher_{i}",
            ]
            df1 = df[["LineNo", f"max_watcher_{i}"]]
            df2 = df[["LineNo", f"line_{i}"]]

        else:
            temp_df = pd.DataFrame(item)
            temp_df.columns = [
                "LineNo",
                f"line_{i}",
                f"time_watcher_{i}",
                f"max_watcher_{i}",
            ]
            temp_df1 = temp_df[["LineNo", f"max_watcher_{i}"]]
            temp_df2 = temp_df[["LineNo", f"line_{i}"]]
            df1 = pd.merge(df1, temp_df1, on="LineNo", how="outer")
            df2 = pd.merge(df2, temp_df2, on="LineNo", how="outer")
    # collect all line nos
    cols = df1.columns.tolist()
    df1["line"] = find_valid_line(df2)
    df1 = df1[["LineNo", "line"] + cols[1:]]
    df1.iloc[:, 2:] = df1.iloc[:, 2:].shift(-1) * 1000

    df1 = df1[~df1.line.apply(lambda x: x.lstrip().startswith("#placeholder"))]
    df1["LineNo"] = list(range(df1.shape[0]))

    mean_time = df1.iloc[:, 2:].apply(lambda x: mean_excluding_nan_count(x), axis=1)
    std_time = df1.iloc[:, 2:].apply(lambda x: std_excluding_nan_count(x), axis=1)
    df1["mean_time(in ms)"] = mean_time
    df1["std_time(in ms)"] = std_time
    df1 = df1.loc[:, ["LineNo", "line", "mean_time(in ms)", "std_time(in ms)"]]
    return df1


def max_length(df, padding_value):
    """
    Calculate the maximum lengths of columns in a DataFrame along with an additional padding value.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the data.
    padding_value : int
        Additional padding value to add to the maximum lengths.

    Returns
    -------
    list
        A list of maximum lengths for each column, considering the original column name length and data length.

    Notes
    -----
    This function computes the maximum lengths required for each column in the provided DataFrame
    along with an additional padding value. It is typically used to format output for display.

    """
    max_list = []
    for col in df.columns:
        max_list.append(
            max(len(col), max(df.loc[:, col].apply(lambda x: len(str(x)))))
            + padding_value
        )
    return max_list


def display_results(df, total_time, no_iter, fn_name):
    """
    Display tracked function execution results in a well-formatted table.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the calculated mean and standard deviation of execution times for each line.
    total_time : list
        List of total execution times for each iteration.
    no_iter : int
        Number of iterations.
    fn_name : str
        Name of the tracked function.

    Notes
    -----
    This function takes the processed DataFrame of tracked data, along with the total execution times and function
    information, and prints the results in a formatted table. The table includes details about mean and standard
    deviation of execution times for each line, as well as overall statistics for the tracked function.

    """
    df.iloc[:, 2:] = round(df.iloc[:, 2:], 3)
    padding_value = 5
    left_padding = 2
    max_string_length = max_length(df, padding_value)
    print()
    heading = f"{' '*left_padding}| LineNo{' '*(max_string_length[0] - len('LineNo'))}| line{' '*(max_string_length[1] - len('line'))}| mean_time(in ms){' '*(max_string_length[2] - len('mean_time(in ms)'))}| std_time(in ms) |"
    print(f"{' '*left_padding}{'='*(len(heading) - left_padding)}")
    print(
        f"{' '*left_padding}|> Function Name: {fn_name}, #iter: {no_iter}, mean_time(in ms): {round(mean_custom(total_time), 3)}, std_time(in_ms): {round(stddev_custom(total_time), 3)}"
    )
    print(f"{' '*left_padding}{'='*(len(heading) - left_padding)}")
    print(heading)
    print(f"{' '*left_padding}{'='*(len(heading) - left_padding)}")
    for row in df.iterrows():
        text = ""
        for i, j in zip(max_string_length, row[1]):
            text = text + "| " + str(j) + " " * (i - len(str(j)))
        print(" " * left_padding + text)
    print(" " * left_padding + "-" * (len(heading) - left_padding))


def _ss(data):
    """
    Calculate the sum of squared deviations of a sequence of data.

    Parameters
    ----------
    data : iterable
        Sequence of numerical values.

    Returns
    -------
    float
        The calculated sum of squared deviations of the provided data.

    Notes
    -----
    This function computes the sum of squared deviations from the mean of the input sequence of numerical values.
    It is primarily used as a helper function by the `stddev_custom` function to calculate variance.

    """
    c = mean_custom(data)
    ss = sum((x - c) ** 2 for x in data)
    return ss


def mean_custom(data):
    """
    Calculate the sample arithmetic mean of a list of values.

    Parameters
    ----------
    data : list
        List of numerical values.

    Returns
    -------
    float
        The calculated arithmetic mean of the provided data.

    Raises
    ------
    ValueError
        If the input data list is empty.

    Notes
    -----
    This function computes the sample arithmetic mean (average) of the given list of numerical values.
    If the input data list is empty, a ValueError is raised.

    """
    n = len(data)
    if n < 1:
        raise ValueError("mean requires at least one data point")
    return sum(data) / n


def stddev_custom(data, ddof=0):
    """
    Calculate the standard deviation of a list of values.

    Parameters
    ----------
    data : list
        List of numerical values.
    ddof : int, optional
        Delta degrees of freedom. By default, computes the population standard deviation.
        Use `ddof=1` to compute the sample standard deviation.

    Returns
    -------
    float
        The calculated standard deviation of the provided data.

    Raises
    ------
    ValueError
        If the input data list has fewer than two data points.

    Notes
    -----
    This function calculates the standard deviation of the given list of numerical values.
    The `ddof` parameter controls whether the population or sample standard deviation is calculated.
    If the input data list has fewer than two data points, a ValueError is raised.

    """
    n = len(data)
    if n < 2:
        raise ValueError("variance requires at least two data points")
    ss = _ss(data)
    pvar = ss / (n - ddof)
    return pvar ** 0.5
