**Barcode Crossover — README**

**Overview**
- This Nextflow pipeline builds a combined reference from FASTA files, converts BAMs to FASTQ, aligns reads, and runs a classification script to detect barcode crossover events.

**What you need to provide**
- A samplesheet CSV listing your samples and their BAM file paths. The pipeline expects a header and two columns named `sample` and `bam` (example below).
- One or more reference FASTA files (FASTA or compressed FASTA). The pipeline will concatenate them into a single reference.
- The classification script at `scripts/classify_reads.py` will be used by the workflow—ensure it exists and is executable.

**Samplesheet format**
- Example `samplesheet.csv`:

```
sample,bam
sample1,/path/to/sample1.bam
sample2,/path/to/sample2.bam
```

**Requirements**
- Java (for Nextflow)
- Nextflow (https://www.nextflow.io)
- samtools
- minimap2
- Python 3 with any packages required by `scripts/classify_reads.py` (e.g., Biopython, pandas)

Install Python deps (example):

```bash
python -m venv .venv
source .venv/bin/activate    # on Windows PowerShell: .venv\Scripts\Activate
pip install biopython pandas
```

**How to run**
- From the project root (the directory containing `main.nf`), run Nextflow and override parameters as needed.

Basic command using default parameter names from `main.nf`:

```bash
nextflow run . -c nextflow.config --samplesheet samplesheet.csv --refs 'refs/*.fa' -with-report report.html
```

- Replace `samplesheet.csv` with the path to your samplesheet.
- Replace `'refs/*.fa'` with a glob or explicit list of reference FASTA files.
- You may pass absolute or relative paths. Quoting the glob is recommended so the shell doesn't expand it prematurely.

**Example (custom inputs)**

```
nextflow run . --samplesheet /data/my_experiment/samples.csv --refs '/data/refs/human_chr*.fa' --outdir /results/my_run
```

**Outputs**
- `results/reference/combined_reference.fa` — concatenated reference
- `results/fastq/` — FASTQ files produced from BAMs
- `results/aligned/` — sorted BAMs from alignment
- `results/classification/` — per-sample CSV results from `classify_reads.py`

**Troubleshooting**
- If Nextflow complains about missing params, open `main.nf` to check `params` names (`samplesheet`, `refs`) and pass them with `--<name>` on the command line.
- Ensure `samtools`, `minimap2`, and `python3` are in your `PATH` and compatible with your system.

**Next steps / enhancements**
- Add a `nextflow.config` or profiles for cluster/cloud execution.
- Provide example `samplesheet.csv` and small test data in `examples/` for CI.

