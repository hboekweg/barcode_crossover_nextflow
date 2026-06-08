nextflow.enable.dsl=2

params.samplesheet = "samplesheet.csv"
params.refs = "refs/*.fa"

//////////////////////////////////////////////////////
// 1. BUILD REFERENCE (from multiple fasta files)
//////////////////////////////////////////////////////

process BUILD_REFERENCE {

    publishDir "results/reference", mode: 'copy'

    input:
    path refs, arity: '1..*'

    output:
    path "combined_reference.fa"

    script:
    """
    cat ${refs} > combined_reference.fa
    """
}

//////////////////////////////////////////////////////
// 2. BAM → FASTQ
//////////////////////////////////////////////////////

process BAM_TO_FASTQ {

    publishDir "results/fastq", mode: 'copy'

    input:
    tuple val(sample), path(bam)

    output:
    tuple val(sample), path("${sample}.fastq")

    script:
    """
    samtools fastq $bam > ${sample}.fastq
    """
}

//////////////////////////////////////////////////////
// 3. ALIGN
//////////////////////////////////////////////////////

process ALIGN {

    publishDir "results/aligned", mode: 'copy'

    input:
    tuple val(sample), path(fastq), path(ref)

    output:
    tuple val(sample), path("${sample}.sorted.bam")

    script:
    """
    minimap2 -t 1 -K 10M -I 1G --split-prefix tmp_index -x map-ont -a \
        $ref $fastq \
    | samtools sort -m 256M -T ${sample} -o ${sample}.sorted.bam
    """
}

//////////////////////////////////////////////////////
// 4. CLASSIFY
//////////////////////////////////////////////////////

process CLASSIFY {

    publishDir "results/classification", mode: 'copy'

    input:
    tuple val(sample), path(bam)
    path script

    output:
    tuple val(sample), path("${sample}.csv")

    script:
    """
    python3 $script \
        --bam $bam \
        --out ${sample}.csv
    """
}

//////////////////////////////////////////////////////
// WORKFLOW
//////////////////////////////////////////////////////

workflow {

    //////////////////////////////////////////////////////
    // Samplesheet → (sample, bam)
    //////////////////////////////////////////////////////

    samples = Channel
        .fromPath(params.samplesheet)
        .splitCsv(header:true)
        .map { row ->
            tuple(row.sample, file(row.bam))
        }

    //////////////////////////////////////////////////////
    // Reference FASTAs → single artifact
    //////////////////////////////////////////////////////

    ref_files = Channel.fromPath(params.refs).collect()

    combined_ref = BUILD_REFERENCE(ref_files)

    //////////////////////////////////////////////////////
    // BAM → FASTQ
    //////////////////////////////////////////////////////

    fastq = BAM_TO_FASTQ(samples)

    //////////////////////////////////////////////////////
    // Attach reference to each FASTQ
    //////////////////////////////////////////////////////

    aligned_input = fastq.combine(combined_ref)

    aligned = aligned_input.map { sample, fq, ref ->
        tuple(sample, fq, ref)
    }

    //////////////////////////////////////////////////////
    // ALIGN
    //////////////////////////////////////////////////////

    bam = ALIGN(aligned)

    //////////////////////////////////////////////////////
    // CLASSIFY
    //////////////////////////////////////////////////////

    CLASSIFY(bam, file("scripts/classify_reads.py"))
}
