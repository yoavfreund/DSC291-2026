#!/usr/bin/env python3
import re

with open('03_dask_delayed_futures.tex', 'r') as f:
    content = f.read()

# Fix 1: Change lstset to use smaller font
content = content.replace(
    'basicstyle=\\ttfamily\\footnotesize,',
    'basicstyle=\\ttfamily\\scriptsize,'
)

# Fix 2: Fix "The Problem" frame - reduce spacing and fix TikZ
content = re.sub(
    r'(\\begin\{frame\}\{The Problem\}[^}]+\\vspace\{0\.3cm\})',
    r'\\begin{frame}\\small\nThe Problem:\n\\begin{itemize}',
    content,
    flags=re.DOTALL
)

# Fix 3: Fix "Basic Delayed Example" - split into two slides
basic_example_match = re.search(
    r'(\\begin\{frame\}\[fragile\]\{Basic Delayed Example\}.+?\\end\{frame\})',
    content,
    flags=re.DOTALL
)

if basic_example_match:
    # Split this slide
    old_slide = basic_example_match.group(1)
    new_slide1 = '''\\begin{frame}[fragile]\\small
Basic Delayed Example: Code
\\begin{lstlisting}
from dask import delayed

@delayed
def inc(x):
    return x + 1

# Returns Delayed object (no execution yet)
result = inc(1)
print(result)  # <Delayed 'inc-...'>

# Actually executes
final = result.compute()
print(final)  # 2
\\end{lstlisting}
\\end{frame}

\\begin{frame}\\small
Basic Delayed Example: Key Points
\\textbf{Key Points:}
\\begin{itemize}
    \\item Simple function decoration
    \\item Returns Delayed object immediately
    \\item Execution happens at \\texttt{.compute()}
\\end{itemize}

\\vspace{0.2cm}
\\textbf{Timeline:}
\\begin{enumerate}
    \\item \\texttt{@delayed} decorates function
    \\item Function call returns Delayed object
    \\item \\texttt{.compute()} triggers execution
\\end{enumerate}
\\end{frame}'''
    content = content.replace(old_slide, new_slide1)

# Fix 4: Fix "Delayed: Multiple Functions" - expand TikZ with explicit positioning
content = re.sub(
    r'(\\begin\{tikzpicture\}\[node distance=1\.2cm, auto, scale=0\.85, every node/\.style=\{font=\\footnotesize\}\]\s+% Input nodes\s+\\node\[draw, rectangle, fill=blue!20\] \(inc1\) \{inc\(1\)\};\s+\\node\[draw, rectangle, fill=blue!20, below of=inc1\] \(inc2\) \{inc\(2\)\};.+?\\end\{tikzpicture\})',
    '''\\begin{tikzpicture}[scale=0.7, every node/.style={font=\\scriptsize}]
    % Input nodes - explicit positioning
    \\node[draw, rectangle, fill=blue!20, text width=1.2cm, align=center] (inc1) at (-2,1) {inc(1)};
    \\node[draw, rectangle, fill=blue!20, text width=1.2cm, align=center] (inc2) at (-2,-0.5) {inc(2)};
    
    % Add node - more space
    \\node[draw, rectangle, fill=green!20, text width=1.5cm, align=center] (add) at (0.5,0.25) {add(3, 4)};
    
    % Result node - more space
    \\node[draw, rectangle, fill=red!20, text width=1.2cm, align=center] (result) at (3,0.25) {result};
    
    % Edges
    \\draw[->, thick] (inc1) -- (add);
    \\draw[->, thick] (inc2) -- (add);
    \\draw[->, thick] (add) -- (result);
\\end{tikzpicture}''',
    content,
    flags=re.DOTALL
)

# Fix 5: Fix "Delayed: For Loops" - split slide and expand TikZ
for_loops_match = re.search(
    r'(\\begin\{frame\}\[fragile\]\{Delayed: For Loops\}.+?\\end\{frame\})',
    content,
    flags=re.DOTALL
)

if for_loops_match:
    old_slide = for_loops_match.group(1)
    new_slide = '''\\begin{frame}[fragile]\\small
Delayed: For Loops
\\textbf{Parallelizing Loops:}
\\begin{lstlisting}
@delayed
def process_file(filename):
    data = read_file(filename)
    return transform(data)

# Create list of delayed tasks
results = [process_file(f) for f in files]

# Execute all in parallel
final = dask.compute(*results)
\\end{lstlisting}
\\end{frame}

\\begin{frame}\\small
Delayed: For Loops - Visualization
\\textbf{Key Advantage:}
\\begin{itemize}
    \\item Loop iterations run in parallel
    \\item Much faster than sequential loop
    \\item Automatic dependency handling
\\end{itemize}

\\vspace{0.1cm}
\\begin{center}
\\begin{tikzpicture}[scale=0.65, every node/.style={font=\\scriptsize}]
    % Sequential - explicit positioning
    \\node[text width=2.5cm, align=center, font=\\small] (seq-label) at (-3,2) {\\textbf{Sequential (slow):}};
    \\node[draw, rectangle, fill=blue!20, text width=1cm, align=center] (f1) at (-4,0.5) {file1};
    \\node[draw, rectangle, fill=blue!20, text width=1cm, align=center] (f2) at (-3,0.5) {file2};
    \\node[draw, rectangle, fill=blue!20, text width=1cm, align=center] (f3) at (-2,0.5) {file3};
    \\draw[->, thick] (f1) -- (f2);
    \\draw[->, thick] (f2) -- (f3);
    
    % Parallel - explicit positioning
    \\node[text width=2.5cm, align=center, font=\\small] (par-label) at (3,2) {\\textbf{Parallel (fast):}};
    \\node[draw, rectangle, fill=green!20, text width=1cm, align=center] (p1) at (2,0.5) {file1};
    \\node[draw, rectangle, fill=green!20, text width=1cm, align=center] (p2) at (3,0.5) {file2};
    \\node[draw, rectangle, fill=green!20, text width=1cm, align=center] (p3) at (4,0.5) {file3};
    \\draw[<->, thick, dashed] (p1) -- (p2);
    \\draw[<->, thick, dashed] (p2) -- (p3);
\\end{tikzpicture}
\\end{center}
\\end{frame}'''
    content = content.replace(old_slide, new_slide)

# Fix 6: Fix "What are Futures?" - expand TikZ with explicit positioning
content = re.sub(
    r'(\\begin\{tikzpicture\}\[node distance=1\.2cm, auto, scale=0\.85, every node/\.style=\{font=\\footnotesize\}\]\s+% Time 0.+?\\end\{tikzpicture\})',
    '''\\begin{tikzpicture}[scale=0.7, every node/.style={font=\\scriptsize}]
    % Time 0 - explicit positioning
    \\node[draw, rectangle, fill=blue!20, text width=2cm, align=center] (submit) at (-2,2) {Submit task};
    \\node[draw, rectangle, fill=yellow!20, text width=2cm, align=center] (pending) at (1,2) {Future\\\\ (pending)};
    \\draw[->, thick] (submit) -- node[above, font=\\tiny] {Time 0} (pending);
    
    % Time 1 - explicit positioning
    \\node[draw, rectangle, fill=orange!20, text width=2cm, align=center] (exec) at (-0.5,0) {Task executing};
    \\node[below of=exec, yshift=0.2cm, font=\\tiny] {Time 1};
    
    % Time 2 - explicit positioning
    \\node[draw, rectangle, fill=green!20, text width=2cm, align=center] (done) at (-2,-2) {Task done};
    \\node[draw, rectangle, fill=green!20, text width=2cm, align=center] (finished) at (1,-2) {Future\\\\ (finished)};
    \\draw[->, thick] (done) -- node[above, font=\\tiny] {Time 2} (finished);
    
    % Vertical flow
    \\draw[->, thick, dashed] (pending) -- (exec);
    \\draw[->, thick, dashed] (exec) -- (done);
\\end{tikzpicture}''',
    content,
    flags=re.DOTALL
)

# Fix 7: Fix "Futures: Map Pattern" - expand TikZ with explicit positioning
content = re.sub(
    r'(\\begin\{tikzpicture\}\[node distance=1\.2cm, auto, scale=0\.85, every node/\.style=\{font=\\footnotesize\}\]\s+% File list.+?\\end\{tikzpicture\})',
    '''\\begin{tikzpicture}[scale=0.7, every node/.style={font=\\scriptsize}]
    % File list - explicit positioning
    \\node[draw, rectangle, fill=blue!20, text width=2.5cm, align=center] (files) at (0,3) {file\\_list:\\\\ f1, f2, f3};
    
    % Map operation - explicit positioning
    \\node[draw, rectangle, fill=orange!20, text width=2.5cm, align=center] (map) at (0,1.5) {map(process\\_file)};
    
    % Futures - explicit positioning
    \\node[draw, rectangle, fill=yellow!20, text width=2.5cm, align=center] (futures) at (0,0) {futures:\\\\ F1, F2, F3};
    
    % Gather operation - explicit positioning
    \\node[draw, rectangle, fill=orange!20, text width=2.5cm, align=center] (gather) at (0,-1.5) {gather};
    
    % Results - explicit positioning
    \\node[draw, rectangle, fill=green!20, text width=2.5cm, align=center] (results) at (0,-3) {results:\\\\ r1, r2, r3};
    
    % Edges
    \\draw[->, thick] (files) -- (map);
    \\draw[->, thick] (map) -- (futures);
    \\draw[->, thick] (futures) -- (gather);
    \\draw[->, thick] (gather) -- (results);
\\end{tikzpicture}''',
    content,
    flags=re.DOTALL
)

# Fix 8: Fix "Combining Delayed and Futures" - expand TikZ
content = re.sub(
    r'(\\begin\{tikzpicture\}\[node distance=1\.2cm, auto, scale=0\.85, every node/\.style=\{font=\\footnotesize\}\]\s+% Outer delayed graph.+?\\end\{tikzpicture\})',
    '''\\begin{tikzpicture}[scale=0.7, every node/.style={font=\\scriptsize}]
    % Outer delayed graph - explicit positioning
    \\node[draw, rectangle, fill=blue!20, text width=3cm, align=center, minimum height=1.2cm] (outer) at (0,1) {\\textbf{Outer:}\\\\ Delayed graph\\\\ (optimized)};
    
    % Inner futures - explicit positioning
    \\node[draw, rectangle, fill=green!20, text width=3cm, align=center, minimum height=1.2cm] (inner) at (0,-1) {\\textbf{Inner:}\\\\ Futures\\\\ (immediate)};
    
    % Connection
    \\draw[<->, thick, dashed] (outer.south) -- (inner.north);
\\end{tikzpicture}''',
    content,
    flags=re.DOTALL
)

# Write the fixed file
with open('03_dask_delayed_futures.tex', 'w') as f:
    f.write(content)

print("Fixed file written successfully!")
