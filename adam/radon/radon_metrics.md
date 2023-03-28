
### Analyze source code lines
>  radon.raw.analyze(source)
- **loc:** The number of lines of code (total)
- **lloc:** The number of logical lines of code

- **sloc:** The number of source lines of code (not necessarily
    corresponding to the LLOC)

- **comments:** The number of Python comment lines
- multi: The number of lines which represent multi-line strings

- **single_comments:** The number of lines which are just comments with
    no code

- **blank:** The number of blank lines (or whitespace-only ones)

## Halstead
> https://www.wikiwand.com/en/Halstead_complexity_measures

h1 = the number of distinct operators
h2 = the number of distinct operands
N1 = the total number of operators
N2 = the total number of operands

vocabulary: h = h1+h2
length: N = N1 + N2
Calculated length: n1 log2 n1 + n2 log2 n2
Volume: V = N * log2 h
Difficulty: D= h1/2 * N2/h2
Effort: E = D * V
Time: T = E/18
bugs E^(2/3)/3000 or B= V/3000
