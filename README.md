# ibaqpy

[![Python application](https://github.com/bigbio/ibaqpy/actions/workflows/python-app.yml/badge.svg)](https://github.com/bigbio/ibaqpy/actions/workflows/python-app.yml)
[![Upload Python Package](https://github.com/bigbio/ibaqpy/actions/workflows/python-publish.yml/badge.svg)](https://github.com/bigbio/ibaqpy/actions/workflows/python-publish.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/6a1961c7d57c4225b4891f73d58cac6b)](https://app.codacy.com/gh/bigbio/ibaqpy/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![PyPI version](https://badge.fury.io/py/ibaqpy.svg)](https://badge.fury.io/py/ibaqpy)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ibaqpy)

iBAQ (Intensity-Based Absolute Quantification) determines the abundance of a protein by dividing the total precursor intensities by the number of theoretically observable peptides of the protein [manuscript here](https://pubmed.ncbi.nlm.nih.gov/16219938/). ibaqpy is a Python package that computes iBAQ values, and other normalized IBAQ values and starting from a feature parquet from [quantmsio](https://github.com/bigbio/quantms.io) and a [SDRF](https://github.com/bigbio/proteomics-sample-metadata) file. 

Additionally, the tool allows computing the TPA value (Total Protein Approach). TPA is determined by summing peptide intensities of each protein and then dividing by the molecular mass to determine the relative concentration of each protein. By using [ProteomicRuler](https://www.sciencedirect.com/science/article/pii/S1535947620337749), it is possible to calculate the protein copy number and absolute concentration.

### Overview of ibaq-base values computation

As mentioned before, ibaq values are calculated by dividing the total precursor intensities by the number of theoretically observable peptides of the protein. We use the following steps to calculate the iBAQ values:

- _Observable peptides_, the protein sequence is digested in silico using a specific enzyme. The current version of this tool uses OpenMS method to load fasta file, and use [ProteaseDigestion](https://openms.de/current_doxygen/html/classOpenMS_1_1ProteaseDigestion.html) to enzyme digestion of protein sequences, and finally get the theoretical peptide number of each protein.

- _Total precursor intensities_, the total intensity of a protein is calculated by summing the intensity of all peptides that belong to the protein. The intensity values are obtained from the feature parquet file in [quantms.io](https://github.com/bigbio/quantms.io).

#### IBAQ calculation

First, peptide intensity dataframe was grouped according to `protein name`, `sample name` and `condition`. Finally, the sum of the intensity of the protein is divided by the number of theoretical peptides.

# TODO: @PingZheng Can you double-check that for protein group we multiply the intensity or divided? 

> Note: If protein-group exists in the peptide intensity dataframe, the intensity of all proteins in the protein-group is summed based on the above steps, and then multiplied by the number of proteins in the protein-group.

#### IBAQ Normalization  

- `IbaqNorm` - normalize the ibaq values using the total ibaq of the sample `ibaq / sum(ibaq)`, the sum is applied for proteins in the same _sample + condition_.
- `IbaqLog`  - The ibaq log is calculated as `10 + log10(IbaqNorm)`. This normalized ibaq value was developed [by ProteomicsDB Team](https://academic.oup.com/nar/article/46/D1/D1271/4584631).
- `IbaqPpb` - The resulted IbaqNorm is multiplied by 100M `IbaqNorm * 100'000'000`. This method was developed originally [by PRIDE Team](https://www.nature.com/articles/s41597-021-00890-2).

### Assemble peptides as proteins

In the sample, the protein was combined from its unique peptides; then the iBAQ value was calculated as the Intensity of the protein divided by the theoretical number of unique peptides cut by the enzyme. This command also normalized iBAQ as riBAQ. See details in `peptides2proteins`.

**Compute TPA**: Compute TPA values, protein copy numbers and concentration from the output file from script `commands/features2peptides`. See details in `commands/compute_tpa.py`.

**Merge projects**: Merge ibaq results from multiple datasets. It consists of three steps: missing value imputation, outlier removal, and batch effect removal. See details in `commands/datasets_merger.py`.

> Note: In all scripts and result files, *uniprot accession* is used as the protein identifier.

![Ibaq](./data/ibaqpy.png "IBAQ")

### How to install ibaqpy

Ibaqpy is available in PyPI and can be installed using pip:

```asciidoc
pip install ibaqpy
```

You can install the package from code:

1. Clone the repository:

```asciidoc
>$ git clone https://github.com/bigbio/ibaqpy
>$ cd ibaqpy
```

2. Install conda environment:

```asciidoc
>$ mamba env create -f conda-environment.yaml
```

3. Install ibaqpy:

```asciidoc
>$ python setup.py install
```

### Collecting intensity files

Absolute quantification files has been store in the following url:

```
http://ftp.pride.ebi.ac.uk/pub/databases/pride/resources/proteomes/absolute-expression/quantms-data/
```

Inside each project reanalysis folder, the folder proteomicslfq contains the msstats input file with the structure `{Name of the project}.{Random uuid}.feature.parquet	`. 

E.g. http://ftp.pride.ebi.ac.uk/pub/databases/pride/resources/proteomes/absolute-expression/quantms-data/MSV000079033.1/MSV000079033.1-bd44c7e3-654c-444d-9e21-0f701d6dac94.feature.parquet

### Assemble features as peptides

```asciidoc
python commands/features2peptides.py -p tests/PXD003947/PXD003947-featrue.parquet -s tests/PXD003947/PXD003947.sdrf.tsv --remove_ids data/contaminants_ids.tsv --remove_decoy_contaminants --remove_low_frequency_peptides --output tests/PXD003947/PXD003947-peptides-norm.csv --log2 --save_parquet
```
```asciidoc
Usage: features2peptides.py [OPTIONS]

Options:
  -p, --parquet TEXT              Parquet file import generated by quantms.io
  -s, --sdrf TEXT                 SDRF file import generated by quantms
  --min_aa INTEGER                Minimum number of amino acids to filter
                                  peptides
  --min_unique INTEGER            Minimum number of unique peptides to filter
                                  proteins
  --remove_ids TEXT               Remove specific protein ids from the
                                  analysis using a file with one id per line
  --remove_decoy_contaminants     Remove decoy and contaminants proteins from
                                  the analysis
  --remove_low_frequency_peptides
                                  Remove peptides that are present in less
                                  than 20% of the samples
  --output TEXT                   Peptide intensity file including other all
                                  properties for normalization
  --skip_normalization            Skip normalization step
  --nmethod TEXT                  Normalization method used to normalize
                                  feature intensities for all samples
                                  (options: mean, median, iqr, none)
  --pnmethod TEXT                 Normalization method used to normalize
                                  peptides intensities for all samples
                                  (options: globalMedian,conditionMedian)
  --log2                          Transform to log2 the peptide intensity
                                  values before normalization
  --save_parquet                  Save normalized peptides to parquet
  --help                          Show this message and exit.
```

Peptide normalization starts from the peptides dataframe extracted from feature parquet. It contains the following columns:

- ProteinName: Protein name
- PeptideSequence: Peptide sequence including post-translation modifications `(e.g. .(Acetyl)ASPDWGYDDKN(Deamidated)GPEQWSK)`
- PrecursorCharge: Precursor charge
- FragmentIon: Fragment ion
- ProductCharge: Product charge
- IsotopeLabelType: Isotope label type
- Condition: Condition label `(e.g. heart)`
- BioReplicate: Biological replicate index `(e.g. 1)`
- Run: Run index `(e.g. 1)`
- Fraction: Fraction index `(e.g. 1)`
- Intensity: Peptide intensity
- Reference: Name of the RAW file containing the peptide intensity `(e.g. Adult_Heart_Gel_Elite_54_f16)`
- SampleID: Sample ID `(e.g. PXD003947-Sample-3)`
- StudyID: Study ID `(e.g. PXD003947)`. In most of the cases the study ID is the same as the ProteomeXchange ID.

#### 1. Data preprocessing

In this section, ibaqpy will do: 
- Remove lines where intensity or study condition is empty
- Parse the identifier of proteins and retain only unique peptides
- Low confidence proteins were removed according to the threshold of unique peptides (optional)
- Filter decoy, contaminants, entrapments, and user-specified proteins (optional)
- Remove peptides with low frequency if `sample number > 1` (optional)
- Data logization (optional)

#### 2. Feature normalization

In this section, ibaqpy corrects the intensity of each MS runs in the sample, eliminating the effect between runs (including technique repetitions). It will do:

- When `MS runs > 1` in the sample, the `mean` of all average(`mean`, `median` or `iqr`) in each MS run is calculated(SampleMean)
- The ratio between SampleMean and the average MS run is used as reference to scale the original intensity

#### 3. Assembly features to peptides

A peptidoform is a combination of a `PeptideSequence(Modifications) + Charge + BioReplicate + Fraction`, and a peptide is a combination of a `PeptideSequence(Canonical) + BioReplicate`. ibaqpy will do:

- Select peptidoforms with the highest intensity across different modifications, fractions, and technical repeats
- Merge peptidoforms across different charges and combined into peptides

#### 4. Peptide Intensity Normalization

Finally, the intensity of the peptide was normalized globally by `globalMedian`,`conditionMedian`.


### Compute IBAQ
IBAQ is an absolute quantitative method based on strength that can be used to estimate the relative abundance of proteins in a sample. IBAQ value is the total intensity of a protein divided by the number of theoretical peptides.

```asciidoc
python commands/peptides2proteins.py --fasta tests/PXD003947/Homo-sapiens-uniprot-reviewed-contaminants-decoy-202210.fasta --peptides tests/PXD003947/PXD003947-peptides-norm.csv --enzyme Trypsin --output tests/PXD003947/PXD003947-ibaq-norm.csv --normalize --verbose
``` 

The command provides an additional `flag` for normalize IBAQ values.

```asciidoc
Usage: peptides2proteins.py [OPTIONS]

Options:
  -f, --fasta TEXT     Protein database to compute IBAQ values
  -p, --peptides TEXT  Peptide identifications with intensities following the
                       peptide intensity output
  -e, --enzyme TEXT    Enzyme used during the analysis of the dataset
                       (default: Trypsin)
  -n, --normalize      Normalize IBAQ values using by using the total IBAQ of
                       the experiment
  --min_aa INTEGER     Minimum number of amino acids to consider a peptide
  --max_aa INTEGER     Maximum number of amino acids to consider a peptide
  -o, --output TEXT    Output file with the proteins and ibaq values
  --verbose            Print addition information about the distributions of
                       the intensities, number of peptides remove after
                       normalization, etc.
  --qc_report TEXT     PDF file to store multiple QC images
  --help               Show this message and exit.
```



### Compute TPA
The total protein approach (TPA) is a label- and standard-free method for absolute protein quantitation of proteins using large-scale proteomic data. In the current version of the tool, the TPA value is the total intensity of the protein divided by its theoretical molecular mass.

[ProteomicRuler](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4256500/) is a method for protein copy number and concentration estimation that does not require the use of isotope labeled standards. It uses the mass spectrum signal of histones as a "proteomic ruler" because it is proportional to the amount of DNA in the sample, which in turn depends on cell count. Thus, this approach can add an absolute scale to the mass spectrometry readout and allow estimates of the copy number of individual proteins in each cell.

```asciidoc
python commands/compute_tpa.py --fasta Homo-sapiens-uniprot-reviewed-contaminants-decoy-202210.fasta --organism 'human' --peptides PXD003947-peptides.csv --ruler --ploidy 2 --cpc 200 --output PXD003947-tpa.tsv --verbose
```

```asciidoc
python compute_tpa.py --help
Usage: compute_tpa.py [OPTIONS]

  Compute the protein copy numbers and concentrations according to a file output of peptides with the
  format described in peptide_normalization.py.

  :param fasta: Fasta file used to perform the peptide identification
  :param peptides: Peptide intensity file
  :param organism: Organism source of the data
  :param ruler: Whether to compute protein copy number, weight and concentration.
  :param ploidy: Ploidy number
  :param cpc: Cellular protein concentration(g/L)
  :param output: Output format containing the TPA values, protein copy numbers and concentrations
  :param verbose: Print addition information about the distributions of the intensities, 
                  number of peptides remove after normalization, etc.
  :param qc_report: PDF file to store multiple QC images

Options:
  -f, --fasta TEXT      Protein database to compute IBAQ values  [required]
  -p, --peptides TEXT   Peptide identifications with intensities following the peptide intensity output  [required]
  -m, --organism        Organism source of the data.
  -r, --ruler           Calculate protein copy number and concentration according to ProteomicRuler
  -n, --ploidy          Ploidy number (default: 2)
  -c, --cpc             Cellular protein concentration(g/L) (default: 200)
  -o, --output TEXT     Output format containing the TPA values, protein copy numbers and concentrations
  --verbose             Print addition information about the distributions of the intensities, 
                        number of peptides remove after normalization, etc.
  --qc_report           PDF file to store multiple QC images (default: "TPA-QCprofile.pdf")
  --help                Show this message and exit.
```

#### 1. Calculate the TPA Value
The OpenMS tool was used to calculate the theoretical molecular mass of each protein. Similar to the calculation of IBAQ, the TPA value of protein-group was the sum of its intensity divided by the sum of the theoretical molecular mass.

#### 2. Calculate the Cellular Protein Copy Number and Concentration
The protein copy calculation follows the following formula:
```
protein copies per cell = protein MS-signal *  (avogadro / molecular mass) * (DNA mass / histone MS-signal)
```
For cellular protein copy number calculation, the uniprot accession of histones were obtained from species first, and the molecular mass of DNA was calculated. Then the dataframe was grouped according to different conditions, and the copy number, molar number and mass of proteins were calculated.

In the calculation of protein concentration, the volume is calculated according to the cell protein concentration first, and then the protein mass is divided by the volume to calculate the intracellular protein concentration.

### Datasets Merge
There are batch effects in protein identification and quantitative results between different studies, which may be caused by differences in experimental techniques, conditional methods, data analysis, etc. Here we provide a method to apply batch effect correction.  First to impute ibaq data, then remove outliers using `hdbscan`, and apply batch effect correction using `pycombat`.


```asciidoc
python commands/datasets_merge.py datasets_merge --data_folder ../ibaqpy_test/ --output datasets-merge.csv --verbose
``` 

```asciidoc
python datasets_merge.py --help
Usage: datasets_merge.py [OPTIONS]

  Merge ibaq results from compute_ibaq.py.

  :param data_folder: Data dolfer contains SDRFs and ibaq CSVs.
  :param output: Output file after batch effect removal.
  :param covariate: Indicators included in covariate consideration when datasets are merged.
  :param organism: Organism to keep in input data.
  :param covariate_to_keep: Keep tissue parts from metadata, e.g. 'LV,RV,LA,RA'.
  :param non_missing_percent_to_keep: non-missing values in each group.
  :param n_components: Number of principal components to be computed.
  :param min_cluster: The minimum size of clusters.
  :param min_sample_num: The minimum number of samples in a neighborhood for a point to be considered as a core point.
  :param n_iter: Number of iterations to be performed.
  :param verbose/quiet: Output debug information.

Options:
  Options:
  -d, --data_folder TEXT          Data dolfer contains SDRFs and ibaq CSVs. [required]
  -o, --output TEXT               Output file after batch effect removal. [required]
  -c, --covariate TEXT            Indicators included in covariate consideration when datasets are merged.
  --organism TEXT                 Organism to keep in input data.
  --covariate_to_keep TEXT        Keep tissue parts from metadata, e.g. 'LV,RV,LA,RA'.
  --non_missing_percent_to_keep FLOAT
                                  non-missing values in each group.
  --n_components TEXT             Number of principal components to be computed.
  --min_cluster TEXT              The minimum size of clusters.
  --min_sample_num TEXT           The minimum number of samples in a neighborhood for a point to be considered as a core point.
  --n_iter TEXT                   Number of iterations to be performed.
  -v, --verbose / -q, --quiet     Output debug information.
  --help                          Show this message and exit.
```

#### 1. Impute Missing Values
Remove proteins missing more than 30% of all samples. Users can keep tissue parts interested, and data will be converted to a expression matrix (samples as columns, proteins as rows), then missing values will be imputed with `KNNImputer`. 

#### 2. Remove Outliers
When outliers are removed, multiple hierarchical clustering is performed using `hdbscan.HDBSCAN`, where outliers are labeled -1 in the PCA plot. When clustering is performed, the default cluster minimum value and the minimum number of neighbors of the core point are the minimum number of samples in all datasets.

*Users can skip this step and do outliers removal manually.*

#### 3. Batch Effect Correction
Using `pycombat` for batch effect correction, and batch is set to `datasets` (refers specifically to PXD ids) and the covariate should be `tissue_part`.

### Citation

Wang H, Dai C, Pfeuffer J, Sachsenberg T, Sanchez A, Bai M, Perez-Riverol Y. Tissue-based absolute quantification using large-scale TMT and LFQ experiments. Proteomics. 2023 Oct;23(20):e2300188. doi: [10.1002/pmic.202300188](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/pmic.202300188). Epub 2023 Jul 24. PMID: 37488995.

### Credits 

- Julianus Pfeuffer
- Yasset Perez-Riverol
- Hong Wang
