import sys
sys.path.insert(0, "/Users/tonymolino/Dropbox/Mac/Desktop/PyProjects/Value_Divergence/Value_Divergence_Code/src")

from make_optimal_a2_graph import run_and_save

src, csv_path, png_path = run_and_save(
    p1x= 1, p1y= 1, p2x= 1, p2y=  4, c1=1.0, c2=1.0,
    min_a1=0.001, max_a1=0.999, n_points=300,  # <- control density here
)
print(src, csv_path, png_path)
