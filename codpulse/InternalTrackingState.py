class InternalState:
    """
    A class for managing internal state information.

    This class maintains private variables related to modified function strings
    and analysis data frames. It provides controlled access to these variables
    through properties and getter/setter methods.

    Parameters
    ----------
    modified_function_string : str
        The modified function string to be stored.

    Attributes
    ----------
    modified_function_string : str
        The modified function string.
    analysis_df : pandas DataFrame or None
        DataFrame containing analysis results, or None if analysis hasn't been performed.

    Methods
    -------
    __getitem__(i)
        Get the modified function string (i=0) or analysis data frame (i=1).
    __setitem__(i, value)
        Set the analysis data frame (i=1) to the given value.

    Examples
    --------
    >>> state = InternalState("x + y")
    >>> state.analysis_df = some_dataframe
    >>> function_string = state[0]
    >>> analysis_data = state[1]
    >>> state[1] = new_dataframe
    """

    def __init__(self, modified_function_string):
        """
        Initialize the InternalState with a modified function string.

        Parameters
        ----------
        modified_function_string : str
            The modified function string to be stored.
        """
        self.modified_function_string = modified_function_string

    @property
    def modified_function_string(self):
        """
        Get the modified function string.

        Returns
        -------
        str
            The modified function string.
        """
        return self.__modified_function_string

    @modified_function_string.setter
    def modified_function_string(self, value):
        """
        Set the modified function string.

        Parameters
        ----------
        value : str
            The modified function string.
        """
        self.__modified_function_string = value

    @property
    def analysis_df(self):
        """
        Get the analysis data frame.

        Returns
        -------
        pandas.DataFrame
            The analysis data frame.
        """
        return self.__analysis_df

    @analysis_df.setter
    def analysis_df(self, value):
        """
        Set the analysis data frame.

        Parameters
        ----------
        value : pandas.DataFrame
            The analysis data frame.
        """
        self.__analysis_df = value

    def __getitem__(self, i):
        """
        Get the modified function string or analysis data frame.

        Parameters
        ----------
        i : int
            Index value, where 0 returns the modified function string and
            1 returns the analysis data frame.

        Returns
        -------
        str or pandas.DataFrame
            The modified function string (i=0) or analysis data frame (i=1).
        """
        if i == 0:
            return self.modified_function_string
        elif i == 1:
            return self.analysis_df

    def __setitem__(self, i, value):
        """
        Set the analysis data frame to the given value.

        Parameters
        ----------
        i : int
            Index value (must be 1 to set the analysis data frame).
        value : pandas.DataFrame
            The new analysis data frame.
        """
        if i == 1:
            self.analysis_df = value
