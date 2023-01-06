import os
import os
import re

import click
import pandas as pd
from typing_extensions import OrderedDict

from ibaqpy_commons import *


def get_mbr_hit(scan: str):
    """
  This function annotates if the peptide is inferred or not by Match between Runs algorithm (1), 0 if the peptide is
  identified in the corresponding file.
  :param scan: scan value
  :return:
  """
    return 1 if pd.isna(scan) else 0


def parse_uniprot_accession(uniprot_id: str) -> str:
    """
    Parse the uniprot accession from the uniprot id in the form of
    tr|CONTAMINANT_Q3SX28|CONTAMINANT_TPM2_BOVIN and convert to CONTAMINANT_TPM2_BOVIN
    :param uniprot_id: uniprot id
    :return: uniprot accession
    """
    uniprot_list = uniprot_id.split(";")
    result_uniprot_list = []
    for accession in uniprot_list:
        if accession.count("|") == 2:
            accession = accession.split("|")[2]
        result_uniprot_list.append(accession)
    return ";".join(result_uniprot_list)


def remove_extension_file(filename: str) -> str:
    """
  The filename can have
  :param filename:
  :return:
  """
    return filename.replace('.raw', '').replace('.RAW', '').replace('.mzML', '')


def get_study_accession(sample_id: str) -> str:
    """
  Get the project accession from the Sample accession. The function expected a sample accession in the following
  format PROJECT-SAMPLEID
  :param sample_id: Sample Accession
  :return: project accessions
  """
    return sample_id.split('-')[0]


def get_run_mztab(ms_run: str, metadata: OrderedDict) -> str:
    """
  Convert the ms_run into a reference file for merging with msstats output
  :param ms_run: ms_run index in mztab
  :param metadata:  metadata information in mztab
  :return: file name
  """
    m = re.search(r"\[([A-Za-z0-9_]+)\]", ms_run)
    file_location = metadata['ms_run[' + str(m.group(1)) + "]-location"]
    file_location = remove_extension_file(file_location)
    return os.path.basename(file_location)


def get_scan_mztab(ms_run: str) -> str:
    """
  Get the scan number for an mzML spectrum in mzTab. The format of the reference
  must be controllerType=0 controllerNumber=1 scan=30121
  :param ms_run: the original ms_run reference in mzTab
  :return: the scan index
  """
    reference_parts = ms_run.split()
    return reference_parts[-1]


def best_probability_error_bestsearch_engine(probability: float) -> float:
    """
  Convert probability to a Best search engine score
  :param probability: probability
  :return:
  """
    return 1 - probability


def print_help_msg(command) -> None:
    """
  Print help information
  :param command: command to print helps
  :return: print help
  """
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))


@click.command()
@click.option("-m", "--msstats", help="MsStats file import generated by quantms", required=True)
@click.option("-s", "--sdrf", help="SDRF file import generated by quantms", required=True)
@click.option("--compress", help="Read all files compress", is_flag=True)
@click.option("-o", "--output", help="Peptide intensity file including other all properties for normalization")
def peptide_file_generation(msstats: str, sdrf: str, compress: bool, output: str) -> None:
    """
    Conversion of peptide intensity information into a file that containers peptide intensities but also
    the metadata around the conditions, the retention time, charge states, etc.

    :param msstats: MsStats file import generated by quantms
    :param sdrf: SDRF file import generated by quantms
    :param compress: Read all files compress
    :param output: Peptide intensity file including other all properties for normalization
  """

    if msstats is None or sdrf is None or output is None:
        print_help_msg(peptide_file_generation)
        exit(1)

    compression_method = 'gzip' if compress else None

    # Read the msstats file
    msstats_df = pd.read_csv(msstats, sep=',', compression=compression_method)
    msstats_df[REFERENCE] = msstats_df[REFERENCE].apply(remove_extension_file)

    msstats_df.rename(
        columns={'ProteinName': PROTEIN_NAME, 'PeptideSequence': PEPTIDE_SEQUENCE, 'PrecursorCharge': PEPTIDE_CHARGE,
                 'Run': RUN,
                 'Condition': CONDITION, 'Intensity': INTENSITY}, inplace=True)

    print(msstats_df)

    msstats_df[PROTEIN_NAME] = msstats_df[PROTEIN_NAME].apply(parse_uniprot_accession)

    # Read the sdrf file
    sdrf_df = pd.read_csv(sdrf, sep='\t', compression=compression_method)
    sdrf_df[REFERENCE] = sdrf_df['comment[data file]'].apply(remove_extension_file)
    print(sdrf_df)

    if FRACTION not in msstats_df.columns:
        msstats_df[FRACTION] = 1
        msstats_df = msstats_df[
            [PROTEIN_NAME, PEPTIDE_SEQUENCE, PEPTIDE_CHARGE, INTENSITY, REFERENCE, CONDITION, RUN,
             BIOREPLICATE, FRACTION, FRAGMENT_ION, ISOTOPE_LABEL_TYPE]]

    # Merged the SDRF with Resulted file
    result_df = pd.merge(msstats_df, sdrf_df[['source name', REFERENCE]], how='left', on=[REFERENCE])
    result_df.rename(columns={'source name': SAMPLE_ID}, inplace=True)

    result_df[STUDY_ID] = result_df[SAMPLE_ID].apply(get_study_accession)

    result_df.to_csv(output, index=False, sep=',')
    print(result_df)


if __name__ == '__main__':
    peptide_file_generation()
