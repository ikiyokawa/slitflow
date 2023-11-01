"""
This module includes functions used in the set_reqs method of the Data class.
The required data must be sorted to align the correspondence between the data.
"""
import sys

import numpy as np
import pandas as pd

if 'ipykernel' in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


def allocate_data(reqs, param):

    index_list = make_index_list(reqs)
    splits_list = make_splits_list(reqs)
    validate_splits(splits_list)

    index_list = add_splits(index_list, splits_list)

    _, index_data_col_list, index_col_max_list = \
        get_index_columns(index_list, splits_list)
    validate_index_columns(index_data_col_list,
                           index_col_max_list, splits_list)

    merged_index_data = filter_and_merge_index_data(
        index_list, splits_list, index_col_max_list[0], param["split_depth"])

    index_list = add_mrg_id(merged_index_data, index_list, index_data_col_list)

    index_list = make_index_dest_setreq(index_list)

    for index, req in zip(index_list, reqs):
        req.split(index=index)

    return reqs


def run_cycle(Data, reqs, param, load_splits, data_splits, run_mode):

    index_list = make_index_list(reqs)
    splits_list = make_splits_list(reqs, load_splits, data_splits)
    validate_splits(splits_list)

    index_list = add_splits(index_list, splits_list)

    _, index_data_col_list, index_col_max_list = \
        get_index_columns(index_list, splits_list)
    validate_index_columns(index_data_col_list,
                           index_col_max_list, splits_list)

    merged_index_data = filter_and_merge_index_data(
        index_list, splits_list, index_col_max_list[0], param["split_depth"])

    index_list = add_mrg_id(merged_index_data, index_list, index_data_col_list)

    merged_index = merge_index_data(index_list)

    load_index = make_load_index(merged_index)

    index_cycle_list, cycle_no_list = make_index_cycle(load_index, index_list)

    save_no_list = make_save_no_list(load_index, merged_index_data)

    for cycle_no, save_no in tqdm(
            zip(cycle_no_list, save_no_list), total=len(cycle_no_list),
            desc="Cyc", leave=False):

        index_data_cycle_list = [
            df.loc[df['_cycle'] == cycle_no] for df in index_cycle_list]

        for req, index_data_cycle in zip(reqs, index_data_cycle_list):

            if len(index_data_cycle) == 0:
                req.clear_data()
                continue

            index_data_cycle_drop = index_data_cycle.drop(
                columns=['_load', '_cycle'])
            file_nos = index_data_cycle_drop['_file'].unique().tolist()

            req.load(file_nos)
            index_split = req.info.index
            index_dest = make_index_dest_cycle(index_split, index_data_cycle)
            req.split(index=index_dest)

        Data.reqs_are_ready = True
        if run_mode == 2:
            Data.run(reqs, param)
        else:
            Data.run_mp(reqs, param)

        if save_no != 0:
            Data.split(param["split_depth"])
            Data.save()


def make_index_list(reqs):
    """Make index list from reqs.
    Initial data: ["_file"]
    Loaded data: ["_file", "_split", "_keep"]
    """

    index_list = []
    for req in reqs:
        index_list.append(req.info.index)
    return index_list


def make_splits_list(reqs, load_splits=None, data_splits=None):
    """Generate a list of splits specifications for each request.
    """

    index_depths = [len(req.info.get_column_name("index")) for req in reqs]
    file_splits = [req.info.split_depth() for req in reqs]

    if load_splits is None:
        load_splits = [req.info.load_split_depth for req in reqs]
    if data_splits is None:
        data_splits = [req.info.data_split_depth for req in reqs]

    return list(zip(index_depths, file_splits, load_splits, data_splits))


def validate_splits(splits_list):
    """Validate the list of splits to ensure they meet specific criteria.
    """

    for splits in splits_list:
        index_depth, file_split, load_split, data_split = splits

        if index_depth < file_split:
            raise ValueError(
                f"Invalid splits detected: {splits}. index_depth should not \
be less than file_split.")

        if load_split is not None and load_split is not None\
                and load_split > data_split:
            raise ValueError(
                f"Invalid splits detected: {splits}. load_split should not be \
greater than data_split.")


def add_splits(index_list, splits_list):
    """Add split columns to a DataFrame based on the provided split values.
    """

    def add_column(index, split_value, col_name):
        """Helper function to add a new column based on the split value."""
        if col_name in index_cols:
            return
        elif split_value is None:
            return
        elif split_value == 0:
            index[col_name] = 1
        elif split_value == 1:
            index[col_name] = index.groupby(
                index_cols[0], sort=False).ngroup() + 1
        else:
            index[col_name] = index.groupby(
                index_cols[:split_value], sort=False).ngroup() + 1

    for index, splits in zip(index_list, splits_list):
        _, file_split, load_split, _ = splits
        if len(index) == 0:
            index = pd.DataFrame({"_file": [1], "_load": [1]})
        else:
            index_cols = index.columns.tolist()
            add_column(index, file_split, "_file")
            add_column(index, load_split, "_load")

    return index_list


def get_index_columns(index_list, splits_list):
    """Extract index columns based on data split values.
    """

    index_col_list = []
    index_data_col_list = []
    for index, splits in zip(index_list, splits_list):
        _, _, _, data_split = splits
        index_col = index.columns.tolist()
        index_col_list.append(index_col)
        index_data_col_list.append(index_col[:data_split])

    max_data_split = max([splits[3] for splits in splits_list])
    index_col_max_list = []
    for index_data_col, splits in zip(index_data_col_list, splits_list):
        _, _, _, data_split = splits
        if data_split == max_data_split:
            index_col_max_list.append(index_data_col)

    return index_col_list, index_data_col_list, index_col_max_list


def validate_index_columns(index_data_col_list, index_col_max_list,
                           splits_list):
    """Validate the consistency of index columns based on the provided lists.
    """

    # Check whether all elements of index_col_max_list are the same
    index_col_max = index_col_max_list[0]
    for index_col in index_col_max_list:
        if index_col != index_col_max:
            raise ValueError("index columns are not consistent.")

    # Check whether all elements of index_data_col are the same with
    # index_col_max up to data_split
    for index_data_col, splits in zip(index_data_col_list, splits_list):
        if index_data_col == [] or splits[3] == 0:
            continue
        if index_data_col != index_col_max[:splits[3]]:
            raise ValueError("index columns are not consistent.")


def filter_and_merge_index_data(index_list, splits_list, index_col_max,
                                save_split=None):
    """Filter and merge index based on the provided lists of index and splits.

    """

    def filter_rows_with_condition(df, col_list):
        """Iteratively remove rows based on a list of columns.

        For each adjacent pair of columns in the list (primary and secondary),
        remove rows where the value in the primary column has a non-NaN value
        in the secondary column but is NaN in the current row.
        """

        df_to_filter = df.copy()

        for i in range(len(col_list) - 1):
            primary_col = col_list[i]
            secondary_col = col_list[i + 1]

            unique_values_with_non_na = df_to_filter[
                df_to_filter[secondary_col].notna()][primary_col].unique()

            condition = df_to_filter[primary_col].isin(
                unique_values_with_non_na) & df_to_filter[secondary_col].isna()
            df_to_filter = df_to_filter[~condition]

        return df_to_filter

    # Main logic of filter_and_merge_index_data starts here
    index_data_list = []

    for index, splits in zip(index_list, splits_list):
        _, _, _, data_split = splits
        if data_split == 0:
            index_data_list.append(pd.DataFrame())
        else:
            index_data = index.loc[:, index.columns[:data_split]]
            index_data = index_data.drop_duplicates().reset_index(drop=True)
            index_data_list.append(index_data)

    merged_index_data = pd.concat(index_data_list)
    merged_index_data = filter_rows_with_condition(
        merged_index_data, index_col_max)

    merged_index_data = merged_index_data.sort_values(
        by=index_col_max).drop_duplicates().reset_index(drop=True)
    merged_index_data['_mrg_id'] = range(1, len(merged_index_data) + 1)

    # add _save column to merged_df
    if save_split is None:
        merged_index_data["_save"] = 0
    elif save_split == 0:
        merged_index_data["_save"] = 1
    elif save_split == 1:
        merged_index_data["_save"] = merged_index_data.groupby(
            index_col_max[0], sort=False).ngroup() + 1
    else:
        merged_index_data["_save"] = merged_index_data.groupby(
            index_col_max[:save_split], sort=False).ngroup() + 1

    return merged_index_data


def add_mrg_id(merged_df, index_list, index_data_col_list):
    """Add a '_mrg_id' column to each DataFrame in index_list.
    """

    sorted_dfs = []
    for index, index_data_col in zip(index_list, index_data_col_list):

        if len(index_data_col) == 0:
            mrg_id_column = merged_df[['_mrg_id']].copy()
            # distribute index to all "_mrg_id" rows
            mrg_id_column['_key'] = 1
            index['_key'] = 1
            concatenated_df = pd.merge(
                index, mrg_id_column, on='_key').drop('_key', axis=1)
            sorted_dfs.append(concatenated_df)
            continue

        # Merge the DataFrame to add the '_mrg_id' column
        merged_index_list_df = pd.merge(
            index, merged_df[index_data_col + ['_mrg_id']], on=index_data_col,
            how='outer')

        # Sort the DataFrame based on '_mrg_id' and other columns not starting
        # with '_'
        sort_columns = [
            '_mrg_id'] + [col for col in merged_index_list_df.columns
                          if not col.startswith('_')]
        sorted_df = merged_index_list_df.sort_values(
            by=sort_columns).reset_index(drop=True)

        sorted_dfs.append(sorted_df)

    return sorted_dfs


def make_index_dest_setreq(index_list):
    """Make a list of index DataFrames with '_dest' column added.
    """
    for index in index_list:

        index["_dest"] = index["_mrg_id"]
        index["_dest"] = index["_dest"].where(
            (index["_file"].notna()) & (index["_split"] != 0),
            - index["_dest"])

        index["_file"] = index["_file"].fillna(0).astype(int)
        index["_split"] = index["_split"].fillna(0).astype(int)
        if "_keep" in index.columns:
            index["_keep"] = index["_keep"].fillna(0).astype(int)
        if "_load" in index.columns:
            index.drop(columns=["_load"], inplace=True)
        index.drop(columns=["_mrg_id"], inplace=True)

    return index_list


def merge_index_data(index_list):
    """ Merge and sort index_list based on a common '_mrg_id' column
    """

    merged_df = pd.DataFrame()

    for i, df in enumerate(index_list):

        extracted_df = df[["_file", "_load", "_mrg_id"]]
        unique_extracted_df = extracted_df.drop_duplicates().\
            reset_index(drop=True)

        # Add suffix to column names except for '_mrg_id'
        unique_extracted_df.columns = [
            f"{col}_{i+1}" if col != '_mrg_id' else col
            for col in unique_extracted_df.columns]

        if i == 0:
            merged_df = unique_extracted_df
        else:
            merged_df = pd.merge(
                merged_df, unique_extracted_df, on='_mrg_id', how='outer')

    merged_df = merged_df.fillna(0).astype(int)

    # Reorder columns to bring '_mrg_id' to the front
    cols = ['_mrg_id'] + [col for col in merged_df.columns if col != '_mrg_id']
    merged_df = merged_df[cols]

    return merged_df.sort_values(by='_mrg_id').reset_index(drop=True)


def make_load_index(merged_index):
    """ Extract columns containing '_load' and compute '_cycle' and '_dest'
    """

    # Extract columns with "_load" and "_mrg_id"
    load_columns = [col for col in merged_index.columns if "_load" in col]
    load_index = merged_index[['_mrg_id'] + load_columns].copy()

    # Compute "_cycle" column
    load_index['_cycle'] = load_index.groupby(
        load_columns, sort=False).ngroup() + 1

    # Keep only "_mrg_id" and "_cycle" columns and compute "_dest" column
    load_index = load_index[["_mrg_id", "_cycle"]]
    load_index['_dest'] = load_index.groupby('_cycle').cumcount() + 1

    return load_index


def make_index_cycle(load_index, index_list):
    """Merge each index DataFrame with the load index and make cycle_no list.
    """

    cycle_no_list = load_index["_cycle"].unique().tolist()

    index_cycle_list = []
    for index_data in index_list:
        merged_data = pd.merge(index_data, load_index,
                               on='_mrg_id', how='left')
        index_cycle_list.append(merged_data)

    return index_cycle_list, cycle_no_list


def make_save_no_list(load_index, merged_index_data):
    """ Create a list of '_save' values.
    """

    id_cycle = load_index[["_mrg_id", "_cycle"]]
    id_save = merged_index_data[["_mrg_id", "_save"]]

    # Merge on '_mrg_id' and process the resulting DataFrame
    save_index = pd.merge(id_cycle, id_save, on="_mrg_id", how="left")
    save_index = save_index.drop(
        columns=["_mrg_id"]).drop_duplicates().reset_index(drop=True)

    # If the value of the next row of '_save' is the same, set the '_save' of
    # that row to 0.
    save_index["_save_next"] = save_index["_save"].shift(-1).fillna(0)
    save_index["_save"] = np.where(
        save_index["_save"] == save_index["_save_next"], 0,
        save_index["_save"])
    save_index = save_index.drop(columns=["_save_next"])

    return save_index["_save"].tolist()


def make_index_dest_cycle(index_split, index_data_cycle):
    """Add the _dest column to index_split.
    """

    index_data_cycle = index_data_cycle.drop(
        columns=["_load", '_mrg_id', '_cycle'])
    merge_cols = index_data_cycle.columns.difference(['_dest']).tolist()

    index_dest = pd.merge(index_split, index_data_cycle, on=merge_cols,
                          how='left')
    index_dest['_dest'].fillna(0, inplace=True)
    index_dest['_dest'] = index_dest['_dest'].astype(int)
    if "_load" in index_dest.columns:
        index_dest = index_dest.drop(columns=["_load"])
    return index_dest
