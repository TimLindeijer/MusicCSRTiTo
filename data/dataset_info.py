import h5py


# Load the HDF5 file
file_path = "C:/Users/tmysi/Documents/DAT640/MusicCSRTiTo/data/msd_summary_file.h5"
file = h5py.File(file_path, 'r')

# Explore the file structure
def explore_hdf5_structure(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(f"Dataset: {name} | Shape: {obj.shape} | Datatype: {obj.dtype}")
    elif isinstance(obj, h5py.Group):
        print(f"Group: {name}")

# Recursively go through groups and datasets
file.visititems(explore_hdf5_structure)


# List all top-level groups in the file
print(list(file.keys()))

# Access a specific group or dataset (replace 'group_name' with an actual name)
group = file['musicbrainz']

# List datasets or attributes in this group
print(list(group.keys()))