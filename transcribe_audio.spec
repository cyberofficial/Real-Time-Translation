# -*- mode: python ; coding: utf-8 -*-
import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
import os
import glob

block_cipher = None

# Define CUDA paths
CUDA_PATH = 'C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6'
cuda_bin = os.path.join(CUDA_PATH, 'bin')
cupti_path = os.path.join(CUDA_PATH, 'extras', 'CUPTI', 'lib64')

binaries = []

# Only add DLLs from paths that exist
if os.path.exists(cuda_bin):
    cuda_dlls = glob.glob(os.path.join(cuda_bin, '*.dll'))
    binaries.extend((dll, '.') for dll in cuda_dlls)

if os.path.exists(cupti_path):
    cupti_dlls = glob.glob(os.path.join(cupti_path, '*.dll'))
    binaries.extend((dll, '.') for dll in cupti_dlls)

# Explicitly add critical CUDA DLLs if they exist
critical_dlls = [
    os.path.join(cuda_bin, 'cudart64_12.dll'),
    os.path.join(cuda_bin, 'cublas64_12.dll'),
    os.path.join(cuda_bin, 'cublasLt64_12.dll'),
    os.path.join(cuda_bin, 'cufft64_11.dll'),
    os.path.join(cuda_bin, 'curand64_10.dll'),
    os.path.join(cuda_bin, 'cusolver64_11.dll'),
    os.path.join(cuda_bin, 'cusparse64_12.dll'),
    os.path.join(cuda_bin, 'cudnn_ops_infer64_8.dll'),
    os.path.join(cuda_bin, 'cudnn_cnn_infer64_8.dll'),
    os.path.join(cupti_path, 'cupti64_2024.3.2.dll')
]

for dll in critical_dlls:
    if os.path.exists(dll):
        binaries.append((dll, '.'))

a = Analysis(
    ['transcribe_audio.py'],
    pathex=['.', './modules', './html_data'],
    binaries=binaries,
    datas=[('data_whisper\\Lib\\site-packages\\whisper\\assets\\mel_filters.npz', 'whisper\\assets'),
       ('data_whisper\\Lib\\site-packages\\whisper\\assets\\multilingual.tiktoken', 'whisper\\assets'),
       ('data_whisper\\Lib\\site-packages\\whisper\\assets\\gpt2.tiktoken', 'whisper\\assets'),
       ('html_data\\static\\*', 'html_data\\static\\'),
       ('html_data\\*', 'html_data\\')],
    hiddenimports=['torch', 'numpy', 'sounddevice', 'speech_recognition'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['cookies'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    exclude_binaries=False,
    name='transcribe_audio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=True,
    icon=None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)