%-----------------------------------------------------------------------
% Job saved on 08-Dec-2021 05:37:59 by cfg_util (rev $Rev: 7345 $)
% spm SPM - SPM12 (7771)
% cfg_basicio BasicIO - Unknown
%-----------------------------------------------------------------------
%%
matlabbatch{1}.spm.util.import.dicom.data = {
                                             '/home/mrjacob/Desktop/mri/sub35/SUB35_VARONLY_301021_35301021/AUSAF_IPEK_20211030_140814_703000/T1_MPR_NS_SAG_P2_1MM_ISO_MK_32CH_MODIFIED_0003/SUB35_VARONLY_301021.MR.AUSAF_IPEK.0003.0001.2021.10.30.15.37.21.109375.95957292.IMA'
                                             };
%%
matlabbatch{1}.spm.util.import.dicom.root = 'flat';
matlabbatch{1}.spm.util.import.dicom.outdir = {'/home/mrjacob/Desktop/prep_out/sub35/func'};
matlabbatch{1}.spm.util.import.dicom.protfilter = '.*';
matlabbatch{1}.spm.util.import.dicom.convopts.format = 'nii';
matlabbatch{1}.spm.util.import.dicom.convopts.meta = 0;
matlabbatch{1}.spm.util.import.dicom.convopts.icedims = 0;
matlabbatch{1}.spm.util.cat.vols = {
					'/home/mrjacob/Desktop/prep_out/sub35/func/f35301021-0005-00001-000001-01.nii,1'
				  };
matlabbatch{1}.spm.util.cat.name = 'sub35e1.nii';
matlabbatch{1}.spm.util.cat.dtype = 4;
matlabbatch{1}.spm.util.cat.RT = NaN;
