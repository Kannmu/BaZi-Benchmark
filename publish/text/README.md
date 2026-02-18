# BaZiBench Technical Report

This directory contains the LaTeX source files for the BaZiBench technical report, prepared for submission to arXiv.

## Files

- `Technical Report.tex` - Main LaTeX document
- `references.bib` - Bibliography file
- `Technical Report.pdf` - Compiled PDF document (17 pages)

## Compilation

This document requires **XeLaTeX** for proper Chinese character support.

### Prerequisites

- TeX Live 2020 or later (or MiKTeX with XeLaTeX support)
- Chinese fonts (STSong, STHeiti, STFangsong)

### Compile Instructions

```bash
# Method 1: Using xelatex directly
xelatex "Technical Report.tex"
bibtex "Technical Report"
xelatex "Technical Report.tex"
xelatex "Technical Report.tex"

# Method 2: Using latexmk (recommended)
latexmk -xelatex "Technical Report.tex"
```

### Alternative: Using pdflatex (without Chinese support)

If you don't need Chinese characters in the appendix examples, you can use pdflatex:

```bash
pdflatex "Technical Report.tex"
bibtex "Technical Report"
pdflatex "Technical Report.tex"
pdflatex "Technical Report.tex"
```

## Document Structure

The technical report includes:

1. **Abstract** - Overview of BaZiBench
2. **Introduction** - Motivation and contributions
3. **Related Work** - LLM benchmarks and cultural AI
4. **BaZi Fundamentals** - Background on traditional Chinese metaphysics
5. **Benchmark Design** - Eight task types with detailed descriptions
6. **Dataset Construction** - Data generation pipeline and statistics
7. **Evaluation Framework** - Scoring methods and protocols
8. **Experimental Setup** - Models and implementation details
9. **Results** - Performance tables (placeholders for actual results)
10. **Analysis and Discussion** - Challenges and implications
11. **Conclusion** - Summary and future work
12. **Appendix** - Detailed examples and algorithm pseudocode

## arXiv Submission

For arXiv submission:

1. **Required files:**
   - `Technical Report.tex`
   - `references.bib`
   - Any custom style files (if used)

2. **Compile on arXiv:**
   - Select "XeLaTeX" as the compilation method
   - Ensure all referenced packages are available

3. **Check:**
   - All citations resolve correctly
   - All figures/tables are included
   - No compilation errors or warnings

## Notes

- The document uses `natbib` for citations with `plainnat` style
- Chinese characters are supported via `xeCJK` package
- Results tables contain placeholders (`-`) for actual experimental results
- The document is formatted for standard A4/letter paper with 1-inch margins

## Citation

If you use BaZiBench in your research, please cite:

```bibtex
@misc{bazibench2024,
  title={BaZiBench: A Comprehensive Benchmark for Evaluating Large Language Models on Traditional Chinese BaZi Analysis},
  author={Anonymous Authors},
  year={2024},
  url={https://github.com/Kannmu/BaZi-Benchmark}
}
```

## Contact

For questions or issues regarding the technical report, please open an issue on the [GitHub repository](https://github.com/Kannmu/BaZi-Benchmark).
