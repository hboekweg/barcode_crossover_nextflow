import argparse
import pysam
import pandas as pd


#####################################
# Parse command line arguments
#####################################

parser = argparse.ArgumentParser()

parser.add_argument(
    "--bam",
    required=True,
    help="Input BAM file"
)

parser.add_argument(
    "--out",
    required=True,
    help="Output classification CSV"
)

args = parser.parse_args()


#####################################
# Open BAM
#####################################

bam = pysam.AlignmentFile(
    args.bam,
    "rb"
)


#####################################
# Species classification
#####################################

def contig_to_species(ref):

    if ref is None:

        return "Unmapped"

    if ref.startswith("chr"):

        return "Human"

    if ref.startswith("NC_"):

        return "Rice"

    if ref == "lambda":

        return "Lambda phage"

    if ref == "D5405":

        return "D5405"

    return "Other"


#####################################
# Iterate reads
#####################################

records=[]

for read in bam:

    if read.is_secondary:

        continue

    if read.is_supplementary:

        continue

    ref = read.reference_name

    mapq = read.mapping_quality

    species = contig_to_species(
        ref
    )

    if read.is_unmapped:

        cls="unmapped"

    elif mapq < 20:

        cls="ambiguous"

    elif species=="D5405":

        cls="correct"

    else:

        cls="crossover"


    records.append({

        "read_id":
            read.query_name,

        "species":
            species,

        "contig":
            ref,

        "mapq":
            mapq,

        "classification":
            cls

    })


#####################################
# Save results
#####################################

df = pd.DataFrame(
    records
)

#what is the percentage of reads that are classified as correct, crossover, ambiguous, and unmapped?
classification_counts = df["classification"].value_counts()
classification_percentages = classification_counts / len(df) * 100

result = pd.DataFrame({
    "classification": classification_counts.index,
    "count": classification_counts,
    "percentage": classification_percentages
})

# result.to_csv("classification_stats.csv")

# result.to_csv("classification_stats.csv", index=False)

result.to_csv(
    args.out,
    index=False
)

print(
    f"Wrote {len(df)} reads to {args.out}"
)


# import pysam
# import pandas as pd


# bam = pysam.AlignmentFile("protocolA.sorted.bam", "rb")
# # bam = pysam.AlignmentFile("protocolB.sorted.bam", "rb")


# def contig_to_species(ref):
#     if ref is None:
#         return "Unmapped"

#     if ref.startswith("chr"):
#         return "Human"

#     if ref.startswith("NC_"):
#         return "Rice"

#     if ref == "lambda":
#         return "Lambda phage"

#     if ref == "D5405":
#         return "D5405"

#     return "Other"

# import pysam
# import pandas as pd


# records = []

# for read in bam:

#     if read.is_secondary or read.is_supplementary:
#         continue

#     ref = read.reference_name
#     mapq = read.mapping_quality

#     species = contig_to_species(ref)

#     if read.is_unmapped:
#         cls = "unmapped"

#     elif mapq < 20:
#         cls = "ambiguous"

#     elif species == "D5405":
#         cls = "correct"

#     else:
#         cls = "crossover"

#     records.append({
#         "read_id": read.query_name,
#         "species": species,
#         "contig": ref,
#         "mapq": mapq,
#         "classification": cls
#     })

# df = pd.DataFrame(records)
# # import pdb; pdb.set_trace()

# #write the df to a csv to be used for QC and plotting metrics
# df.to_csv("read_classification_protocolA.csv", index=False)
