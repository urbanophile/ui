import numpy as np
import json
import os


def bin_data(data, bin_amount):
    """
    Returns data where each successive bin_amount data points
    are grouped together
    """

    if bin_amount == 1:
        return data
    # This is part of a generic binning class that I wrote.
    # It lets binning occur of the first axis for any 2D or 1D array
    if len(data.shape) == 1:
        data2 = np.zeros((data.shape[0] // bin_amount))
    else:
        data2 = np.zeros((data.shape[0] // bin_amount, data.shape[1]))

    for i in range(data.shape[0] // bin_amount):
        data2[i] = np.mean(data[i * bin_amount:(i + 1) * bin_amount], axis=0)

    return data2


class OutputData():
    """
    This class handles loading and saving file data
    """

    Path = os.getcwd()
    LoadPath = os.getcwd()

    def save_data(self, data, filename, filepath):
        """
        Writes experimental data to TSV file
        """

        variables = 'Time (s)\tGeneration (V)\tPC (V)\tPL (V)'
        full_path = os.path.join(filepath, filename + '.dat')
        np.savetxt(full_path, data, delimiter='\t', header=variables)

    def save_metadata(self, metadata_dict, filename, filepath):
        """
        Writes experimental metadata to JSON file
        """
        print(metadata_dict, type(metadata_dict))
        assert type(metadata_dict) is dict

        full_path = os.path.join(filepath, filename + '.inf')
        serialised_json = json.dumps(
            metadata_dict,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )

        with open(full_path, 'w') as text_file:
                text_file.write(serialised_json)

    def load_metadata(self, full_filepath):
        """
        Loads metadata file and returns a python dictionary
        """

        with open(full_filepath, 'r') as f:
            file_contents = f.read()
            metadata_dict = json.loads(file_contents)

        return metadata_dict
