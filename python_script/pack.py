import os

bmp2gr_path = r"C:\Users\10947\source\repos\bmp2gr\x64\Release\bmp2gr.exe"
packer_path = r"C:\Users\10947\source\repos\bmp2gr\x64\Release\pak_packer.exe"

out_script_pak = r"D:\SQUEEZ\HSHINTAI2\Script\SCPACK.pak"
out_cg_pak = r"D:\SQUEEZ\HSHINTAI2\CG\CGPACK.pak"

out_cg_folder = r"D:\SQUEEZ\HSHINTAI2\CG"

# os.system(f"{bmp2gr_path} new_bm new_gr2")
# os.system(f"{bmp2gr_path} new_bm {out_cg_folder}")
# os.system(f"{bmp2gr_path} new_bm2 new_gr")

# os.system(f"{packer_path} old_dat {out_script_folder}")
# os.system(f"{packer_path} old_gr {out_cg_folder}")

os.system(f"{packer_path} res_dat2 {out_script_pak}")
# os.system(f"{packer_path} new_gr {out_cg_folder}")