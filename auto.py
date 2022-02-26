import time
import nipype.interfaces.matlab as matlab
from nipype.interfaces.dcm2nii import Dcm2nii
import os
import subprocess


def get_direc():
    # fMRI RAW DATA PATH
    subfolders = []
    subjectpath = input("Select your all subject folders and drag into command line and press enter: ")
    if subjectpath == "":
        subjectpath = "'/home/mrjacob/Desktop/mri/sub35' '/home/mrjacob/Desktop/mri/sub36' '/home/mrjacob/Desktop/mri/sub37'"
    for item in subjectpath.split(" "):
        if item != "":
            subfolders.append(item[1:-1])
    subfolders.sort()
    # Matlab PATH
    try:
        matlabpath = subprocess.Popen("which matlab", shell=True,
                                      stdout=subprocess.PIPE).stdout.read().decode().split("\n")[0]
    except:
        matlabpath = "/home/mrjacob/matlab2021b/bin/matlab"
    matlab.MatlabCommand.set_default_paths(matlabpath)

    # SPM PATH
    spmpath = input("Drag your SPM12 folder and press enter: ").strip("'")
    if spmpath == "":
        spmpath = '/home/mrjacob/spm12/'
    if spmpath[-1] == " ":
        spmpath = spmpath[:-1].strip("'")
    matlab.MatlabCommand.set_default_paths(spmpath)

    # MATLAB BATCH AUTOMATION CODE
    codepath = input("Drag your Matlab Automation Batch code file and press enter: ").strip("'")
    if codepath == "":
        codepath = '/home/mrjacob/Desktop/Preprocess_jacob_job.m'
    if codepath[-1] == " ":
        codepath = codepath[:-1].strip("'")
    # codefile = open(codepath, 'r')

    # MATLAB RUN CODE
    jobpath = input("Drag your matlab run file and press enter: ").strip("'")
    if jobpath == "":
        jobpath = '/home/mrjacob/Desktop/Preprocess_jacob.m'
    if jobpath[-1] == " ":
        jobpath = jobpath[:-1].strip("'")

    # DICOM CODE
    dicompath = input("Drag your dicom import code file and press enter: ").strip("'")
    if dicompath == "":
        dicompath = '/home/mrjacob/Desktop/dicom_import_job.m'
    if dicompath[-1] == " ":
        dicompath = dicompath[:-1].strip("'")

    return subfolders, matlabpath, spmpath, codepath, jobpath, dicompath


def check_directories(folders, matlabpath, spmpath, codepath, output, jobpath, dicompath):
    print("__SUBJECTS__")
    for sub in folders:
        print(sub)
    print("\n", "MATLAB", " --> ", matlabpath, "\n")
    print("SPM", " --> ", spmpath, "\n")
    print("CODE", " --> ", codepath, "\n")
    print("OUTPUT", " --> ", output, "\n")
    print("JOB", " --> ", jobpath, "\n")
    print("DICOM JOB", " --> ", dicompath, "\n")


def dicom_to_nii(in_path, out_path):
    converter = Dcm2nii()
    converter.inputs.date_in_filename = False
    for r, d, f in os.walk(in_path):
        source_files = []
        out = ""
        if "MOCO" in r:
            out = "/func"
        elif "T1" in r:
            out = "/anat"
        else:
            continue
        for dicom_item in sorted(os.listdir(r)):
            if ".IMA" in dicom_item:
                source_files.append(dicom_item)
        if len(source_files) != 0:
            os.chdir(r)
            converter.inputs.source_names = source_files
            converter.inputs.output_dir = out_path + out
            converter.run()
        if out == "/anat":
            for item in sorted(os.listdir(out_path + out)):
                if item[:2] == "ot" or item[:3] == "cot":
                    os.remove(out_path + out + "/" + item)


def dicom_to_nii_spm(jobpath, in_path, out_path, dicompath):
    dicom_job = matlab.MatlabCommand()
    dicom_job.inputs.mfile = False
    dicom_job.inputs.nodesktop = False
    for r, d, f in os.walk(in_path):
        d.sort()
        source_files = []
        out = ""
        if "MOCO" in r:
            out = "/func"
        elif "T1" in r:
            out = "/anat"
        else:
            continue
        for dicom_item in sorted(os.listdir(r)):
            if ".IMA" in dicom_item:
                source_files.append(dicom_item)
        if len(source_files) != 0:
            os.chdir(r)
            dicom_script = run_editor(dicompath, out_path, in_path, [r, source_files], out, select="dicom")
            dicom_batch_path = out_path + "/" + in_path.strip("/").split("/")[-1] + "_dicom_batch.m"
            file_handler = open(dicom_batch_path, "w")
            try:
                file_handler.write(dicom_script)
                file_handler.close()
            except:
                file_handler.close()
            script_str = run_editor(jobpath, out_path, in_path, select="dicom_run")
            run_file_path = out_path + "/" + in_path.strip("/").split("/")[-1]+"_run.m"
            file_handler = open(run_file_path, "w")
            try:
                file_handler.write(script_str)
                file_handler.close()
            except:
                file_handler.close()
            dicom_job.inputs.script = "run " + run_file_path
            dicom_job.run()
            if out == "/func":
                script_str = run_editor(dicompath, out_path, in_path, out=out, select="dicom", second_job=True)
                file_handler = open(dicom_batch_path, "w")
                try:
                    file_handler.write(script_str)
                    file_handler.close()
                except:
                    file_handler.close()
                dicom_job.inputs.script = "run " + run_file_path
                dicom_job.run()
                list_files = sorted(os.listdir(out_path + out))
                for item in list_files:
                    skip = False
                    for iteration in range(50):
                        if "e" + str(iteration) in item:
                            skip = True
                    if skip:
                        continue
                    else:
                        os.remove(out_path + out + "/" + item)
            # os.remove(dicom_batch_path)
            # os.remove(run_file_path)


def database_creator(jobpath, subjects, dicompath, dicom=False):
    output_path = input("Drag your empty output folder then press enter [ /home/" +
                        os.getlogin() + "/Desktop/prep_out ] : ").strip("'")
    if output_path == "":
        output_path = "/home/" + os.getlogin() + "/Desktop/prep_out"
    if output_path[-1] == " ":
        output_path = output_path[:-1].strip("'")
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    os.chdir(output_path)
    for subject in subjects:
        out = "/" + subject.split("/")[-1]
        if not os.path.isdir(output_path + out):
            os.mkdir(output_path + out)
        if not os.path.isdir(output_path + out + "/func"):
            os.mkdir(output_path + out + "/func")
        if not os.path.isdir(output_path + out + "/anat"):
            os.mkdir(output_path + out + "/anat")
        if dicom:
            dicom_to_nii_spm(jobpath, subject, output_path + out, dicompath)
    return output_path


def batch_editor(batchpath, subjects, output, spmpath):
    for subject in subjects:
        list_path = os.listdir(output + "/" + subject.strip("/").split("/")[-1] + "/func")
        temp_list_path = list_path.copy()
        func_number = 0
        for item in temp_list_path:
            if ".nii" in item:
                func_number += 1
            else:
                os.remove(output + "/" + subject.strip("/").split("/")[-1] + "/func/" + item)
        batch_file = open(batchpath, 'r')
        base_code = batch_file.read().split(";")
        altered_code = base_code
        tissue_count = 1
        for line_index, line in enumerate(base_code):
            altered_line = altered_code[line_index]
            altered_items = altered_line.split("{")
            if "cfg_basicio.file_dir.file_ops.cfg_named_file.files" in line:
                nii_file_count = 0
                for item_index, line_item in enumerate(line.split("{")):
                    if "nii" in line_item:
                        for func_num in range(func_number):
                            func_nii_path = output + "/" + subject.strip("/").split("/")[-1] + "/func/"
                            func_nii_path += sorted(os.listdir(func_nii_path))[nii_file_count]
                            temp_list = altered_items[item_index].split("'")
                            temp_list[1] = func_nii_path
                            temp_string = "'".join(map(str, temp_list))[:-2]
                            additional = ""
                            if func_num == func_number-1:
                                additional = "}'"
                            altered_items.append(temp_string + additional)
                            nii_file_count += 1
                altered_items.pop(3)
            elif "spm.spatial.realign.estwrite.data" in line:
                new_line = ""
                for func_num in range(func_number):
                    new_line += "{".join(line.split("{")[:2]) + "{" + str(func_num + 1)
                    new_line += line.split("{")[2][1:][:51] + str(func_num + 1) + line.split("{")[2][1:][52:] + "{" + "{".join(line.split("{")[3:12])
                    new_line += "{" + str(func_num + 1) + line.split("{")[12][1:] + ";"
                altered_items = [new_line[:-1]]
            elif "spm.temporal.st.scans" in line:
                new_line = ""
                for func_num in range(func_number):
                    new_line += "{".join(line.split("{")[:2]) + "{" + str(func_num + 1)
                    new_line += line.split("{")[2][1:68] + str(func_num + 1) + line.split("{")[2][69:] + "{" + "{".join(line.split("{")[3:11])
                    new_line += "{" + str(func_num + 1) + line.split("{")[11][1:] + ";"
                altered_items = [new_line[:-1]]
            elif "spatial.coreg.estwrite.source" in line:
                nii_file_count = 0
                for item_index, line_item in enumerate(line.split("{")):
                    if "nii" in line_item:
                        anat_nii_path = output + "/" + subject.strip("/").split("/")[-1] + "/anat/"
                        anat_nii_path += os.listdir(anat_nii_path)[nii_file_count] + ",1"
                        temp_list = altered_items[item_index].split("'")
                        temp_list[1] = anat_nii_path
                        temp_string = "'".join(map(str, temp_list))
                        altered_items[item_index] = temp_string
                        nii_file_count += 1
            elif "spm.spatial.preproc.tissue" in line and ".tpm" in line:
                for item_index, line_item in enumerate(line.split("{")):
                    if "nii" in line_item:
                        tissue = spmpath + "/tpm/TPM.nii," + str(tissue_count)
                        temp_list = altered_items[item_index].split("'")
                        temp_list[1] = tissue
                        temp_string = "'".join(map(str, temp_list))
                        altered_items[item_index] = temp_string
                        tissue_count += 1
            elif "spm.spatial.normalise.write.subj.resample" in line:
                new_line = ""
                for func_num in range(func_number):
                    new_line += line.split("{")[0] + "{" + line.split("{")[1].split(")")[0][:-1] + str(func_num+1) + ")"
                    new_line += line.split("{")[1].split(")")[1][:-1] + str(func_num + 1) + ")" + line.split("{")[1].split(")")[2] + "{"
                    new_line += "{".join(line.split("{")[2:8]) + "{" + str(func_num + 1)
                    new_line += line.split("{")[8][1:] + ";"
                altered_items = [new_line[:-1]]
            new_altered_line = '{'.join(map(str, altered_items))
            altered_code[line_index] = new_altered_line
        new_altered_code = ';'.join(map(str, altered_code))
        file_handler = open(output + "/" + subject.strip("/").split("/")[-1] + "_batch.m", "w")
        try:
            file_handler.write(new_altered_code)
            file_handler.close()
        except:
            file_handler.close()


def run_editor(jobpath, output, subject, dicom_files=None, out=None, select="run", second_job=False):
    if select == "dicom":
        file_handler = open(jobpath, "r")
        job_file = file_handler.read().split("\n")
        if second_job:
            job_file = job_file[16:]
        else:
            job_file = job_file[:15]
        new_job_file = job_file
        for item_index, item in enumerate(job_file):
            if "cat.name =" in item:
                eps_num = 1
                num_list = []
                if len(os.listdir(output + out)) > 0:
                    for num_item in sorted(os.listdir(output + out)):
                        if "sub" in num_item:
                            num_list.append(int(num_item[-5]))
                    if len(num_list) > 0:
                        eps_num = str(int(max(num_list)) + 1)
                new_job_file[item_index] = item.split("=")[0] + "= '" + subject.strip("/").split("/")[-1]
                new_job_file[item_index] += "e" + str(eps_num) + ".nii" + "';"
            elif "dicom.outdir =" in item:
                new_job_file[item_index] = item.split("{")[0] + "{" + item.split("{")[1] + "{'" + output + out + "'};"
            elif ".IMA" in item:
                temp_string = ""
                for one_ima in dicom_files[1]:
                    new_ima = item.split("'")[0] + "'" + dicom_files[0] + "/" + one_ima + "'" + "\n"
                    temp_string += new_ima
                new_job_file[item_index] = temp_string.strip("\n")
            elif ".nii" in item and "cat.name" not in item and second_job:
                temp_string = ""
                threed_files = sorted(os.listdir(output + out))
                for one_threed in threed_files:
                    new_ima = item.split("'")[0] + "'" + output + out + "/" + one_threed + ",1'" + "\n"
                    temp_string += new_ima
                new_job_file[item_index] = temp_string.strip("\n")
        code = '\n'.join(map(str, new_job_file))
        return code
    else:
        file_handler = open(jobpath, "r")
        job_file = file_handler.read().split("\n")
        new_job_file = job_file
        for item_index, item in enumerate(job_file):
            if "jobfile =" in item:
                if select == "dicom_run":
                    new_job_file[item_index] = "jobfile = {'" + output + "/"
                    new_job_file[item_index] += output.split("/")[-1] + "_dicom_batch.m" + "'};"
                else:
                    new_job_file[item_index] = "jobfile = {'" + output + "/"
                    new_job_file[item_index] += subject.split("/")[-1] + "_batch.m" + "'};"
            elif "nrun =" in item:
                new_job_file[item_index] = "nrun = 1;"
        code = '\n'.join(map(str, new_job_file))
        return code


def preprocess(jobpath, outfolder, subfolders, preproces=False):
    prep_job = matlab.MatlabCommand()
    prep_job.inputs.mfile = False
    prep_job.inputs.nodesktop = False
    for subject in subfolders:
        script_str = run_editor(jobpath, outfolder, subject)
        run_file_path = outfolder + "/" + subject.strip("/").split("/")[-1] + "_run.m"
        file_handler = open(run_file_path, "w")
        try:
            file_handler.write(script_str)
            file_handler.close()
        except:
            file_handler.close()
        prep_job.inputs.script = "run " + run_file_path
        if preproces:
            prep_job.run()


def main():
    start_time = time.time()
    do_dicom = input("Do you want to do dicom import? [type 'yes' or 'no' then press enter]: ")
    if do_dicom.strip().lower().strip("'") == "yes":
        do_dicom = True
    else:
        do_dicom = False
    do_preprocess = input("Do you want to do preprocess import? [type 'yes' or 'no' then press enter]: ")
    if do_preprocess.strip().lower().strip("'") == "yes":
        do_preprocess = True
    else:
        do_preprocess = False
    sub_folders, matlab_path, spm_path, code_path, job_path, dicom_path = get_direc()
    out_folder = database_creator(job_path, sub_folders, dicom_path, dicom=do_dicom)
    while True:
        editing = input("Are all files OK before preprocess? [type 'done' then press enter]: ")
        if editing.strip().lower().strip("'") == "done":
            break
    sub_folders, matlab_path, spm_path, code_path, job_path, dicom_path = get_direc()
    batch_editor(code_path, sub_folders, out_folder, spm_path)
    preprocess(job_path, out_folder, sub_folders, preproces=do_preprocess)
    check_directories(sub_folders, matlab_path, spm_path, code_path, out_folder, job_path, dicom_path)
    print("Time spent: ", int(time.time()-start_time), " seconds")


if __name__ == "__main__":
    main()
