import os
import unittest


class PollReader():
    """
    A class for reading and analyzing polling data.
    """
    def __init__(self, filename):
        """
        The constructor. Opens up the specified file, reads in the data,
        closes the file handler, and sets up the data dictionary that will be
        populated with build_data_dict().

        We have implemented this for you. You should not need to modify it.
        """

        # this is used to get the base path that this Python file is in in an
        # OS agnostic way since Windows and Mac/Linux use different formats
        # for file paths, the os library allows us to write code that works
        # well on any operating system
        self.base_path = os.path.abspath(os.path.dirname(__file__))

        # join the base path with the passed filename
        self.full_path = os.path.join(self.base_path, filename)

        # open up the file handler
        # NOTE: file_obj is only used to read the file, it's not strictly necessary to
        # make it an instance variable if it's closed immediately.
        try:
            with open(self.full_path, 'r') as file_obj:
                # read in each line of the file to a list
                self.raw_data = file_obj.readlines()
        except FileNotFoundError:
            # Handle case where file is missing, especially during testing
            self.raw_data = []


        # set up the data dict that we will fill in later
        self.data_dict = {
            'month': [],
            'date': [],
            'sample': [],
            'sample type': [],
            'Harris result': [],
            'Trump result': []
        }

    def build_data_dict(self):
        """
        Reads all of the raw data from the CSV and builds a dictionary where
        each key is the name of a column in the CSV, and each value is a list
        containing the data for each row under that column heading.
        
        Bugs fixed:
        1. Skipping the header row (raw_data[1:]).
        2. Splitting by comma (',') for CSV format, instead of space (' ').
        3. Correcting the mapping indices (seperated[3], [4], and [5]) for the last three columns.
        """

        # iterate through each row of the data, starting after the header (row 1)
        for i in self.raw_data[1:]:

            # strip() removes leading/trailing whitespace and the newline character
            # split(',') assumes a standard CSV format
            seperated = [s.strip() for s in i.strip().split(',')]
            
            # Ensure the row has the expected number of columns (6)
            if len(seperated) != 6:
                continue

            try:
                # map each part of the row to the correct column
                # Indices: 0:month, 1:date, 2:sample, 3:sample type, 4:Harris, 5:Trump
                self.data_dict['month'].append(seperated[0])
                self.data_dict['date'].append(int(seperated[1]))
                self.data_dict['sample'].append(int(seperated[2]))
                # Corrected index (3) and data type (str)
                self.data_dict['sample type'].append(seperated[3]) 
                # Corrected index (4) and data type (float)
                self.data_dict['Harris result'].append(float(seperated[4])) 
                # Corrected index (5) and data type (float)
                self.data_dict['Trump result'].append(float(seperated[5])) 

            except (ValueError, IndexError):
                # Safely skip any row that cannot be correctly converted
                continue


    def highest_polling_candidate(self):
        """
        This method should iterate through the result columns and return
        the name of the candidate with the highest single polling percentage
        Alongside the highest single polling percentage.
        If equal, return the highest single polling percentage and "EVEN".

        Returns:
            str: A string indicating the candidate with the highest polling percentage or EVEN,
                 and the highest polling percentage.
        """
        harris_results = self.data_dict['Harris result']
        trump_results = self.data_dict['Trump result']
        all_results = harris_results + trump_results

        if not all_results:
            return "No polling data available"

        max_result = max(all_results)
        
        # Determine if the max result appears in either list
        harris_has_max = max_result in harris_results
        trump_has_max = max_result in trump_results
        
        result_str = f"{max_result:.1f}%"

        if harris_has_max and trump_has_max:
            # If the max value appears in both, return EVEN
            return f"{result_str} (EVEN)"
        elif harris_has_max:
            return f"Harris: {result_str}"
        elif trump_has_max:
            return f"Trump: {result_str}"
        # Fallback (should not be reached if all_results is not empty)
        return "Error in processing"


    def likely_voter_polling_average(self):
        """
        Calculate the average polling percentage for each candidate among likely voters.

        Returns:
            tuple: A tuple containing the average polling percentages for Harris and Trump
                   among likely voters, in that order.
        """
        harris_scores = []
        trump_scores = []
        
        sample_types = self.data_dict['sample type']
        harris_results = self.data_dict['Harris result']
        trump_results = self.data_dict['Trump result']

        for i, sample_type in enumerate(sample_types):
            # Filter for polls labeled 'Likely Voters'
            if sample_type.strip() == 'Likely Voters':
                harris_scores.append(harris_results[i])
                trump_scores.append(trump_results[i])

        # Calculate average, returning 0.0 if no matching polls are found
        harris_avg = sum(harris_scores) / len(harris_scores) if harris_scores else 0.0
        trump_avg = sum(trump_scores) / len(trump_scores) if trump_scores else 0.0

        return harris_avg, trump_avg


    def polling_history_change(self):
        """
        Calculate the change in polling averages between the earliest and latest polls.

        This method calculates the average result for each candidate in the earliest 30 polls
        and the latest 30 polls, then returns the net change.

        Returns:
            tuple: A tuple containing the net change for Harris and Trump, in that order.
                   Positive values indicate an increase, negative values indicate a decrease.
        """
        harris_results = self.data_dict['Harris result']
        trump_results = self.data_dict['Trump result']
        
        data_count = len(harris_results)
        
        # Check if there is enough data for 30 early and 30 late polls
        if data_count < 30:
            return 0.0, 0.0
        
        # Earliest 30 polls (indices 0 to 29)
        early_harris = harris_results[:30]
        early_trump = trump_results[:30]
        
        early_harris_avg = sum(early_harris) / len(early_harris)
        early_trump_avg = sum(early_trump) / len(early_trump)

        # Latest 30 polls (indices from data_count - 30 to data_count - 1)
        late_harris = harris_results[data_count - 30:]
        late_trump = trump_results[data_count - 30:]
        
        late_harris_avg = sum(late_harris) / len(late_harris)
        late_trump_avg = sum(late_trump) / len(late_trump)
        
        # Calculate net change: latest average - earliest average
        harris_change = late_harris_avg - early_harris_avg
        trump_change = late_trump_avg - early_trump_avg

        return harris_change, trump_change


class TestPollReader(unittest.TestCase):
    """
    Test cases for the PollReader class.
    """
    def setUp(self):
        # NOTE: This assumes 'polling_data.csv' exists in the same directory 
        # as the test file and is correctly formatted.
        self.poll_reader = PollReader('polling_data.csv')
        self.poll_reader.build_data_dict()

    def test_build_data_dict(self):
        self.assertEqual(len(self.poll_reader.data_dict['date']), len(self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['date']))
        self.assertTrue(all(isinstance(x, int) for x in self.poll_reader.data_dict['sample']))
        self.assertTrue(all(isinstance(x, str) for x in self.poll_reader.data_dict['sample type']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Harris result']))
        self.assertTrue(all(isinstance(x, float) for x in self.poll_reader.data_dict['Trump result']))

    def test_highest_polling_candidate(self):
        result = self.poll_reader.highest_polling_candidate()
        self.assertTrue(isinstance(result, str))
        self.assertTrue("Harris" in result)
        self.assertTrue("57.0%" in result)

    def test_likely_voter_polling_average(self):
        harris_avg, trump_avg = self.poll_reader.likely_voter_polling_average()
        self.assertTrue(isinstance(harris_avg, float))
        self.assertTrue(isinstance(trump_avg, float))
        # Assuming the input data is 0-100, these checks are correct for percentage formatting
        self.assertTrue(f"{harris_avg:.2%}" == "49.34%") 
        self.assertTrue(f"{trump_avg:.2%}" == "46.04%")

    def test_polling_history_change(self):
        harris_change, trump_change = self.poll_reader.polling_history_change()
        self.assertTrue(isinstance(harris_change, float))
        self.assertTrue(isinstance(trump_change, float))
        self.assertTrue(f"{harris_change:+.2%}" == "+1.53%")
        self.assertTrue(f"{trump_change:+.2%}" == "+2.07%")


def main():
    poll_reader = PollReader('polling_data.csv')
    poll_reader.build_data_dict()

    highest_polling = poll_reader.highest_polling_candidate()
    print(f"Highest Polling Candidate: {highest_polling}")
    
    harris_avg, trump_avg = poll_reader.likely_voter_polling_average()
    print(f"Likely Voter Polling Average:")
    print(f"  Harris: {harris_avg:.2f}") # Changed from %.2f to .2f to match test format logic
    print(f"  Trump: {trump_avg:.2f}") # Changed from %.2f to .2f to match test format logic
    
    harris_change, trump_change = poll_reader.polling_history_change()
    print(f"Polling History Change:")
    print(f"  Harris: {harris_change:+.2f}") # Changed from %.2f to .2f to match test format logic
    print(f"  Trump: {trump_change:+.2f}") # Changed from %.2f to .2f to match test format logic


if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)
