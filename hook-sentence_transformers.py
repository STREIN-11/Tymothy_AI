from PyInstaller.utils.hooks import collect_all, collect_data_files

datas, binaries, hiddenimports = collect_all('sentence_transformers')

# Also collect transformers data
transformers_datas, transformers_binaries, transformers_hiddenimports = collect_all('transformers')
datas += transformers_datas
binaries += transformers_binaries
hiddenimports += transformers_hiddenimports

# Collect tokenizers
tokenizers_datas, tokenizers_binaries, tokenizers_hiddenimports = collect_all('tokenizers')
datas += tokenizers_datas
binaries += tokenizers_binaries
hiddenimports += tokenizers_hiddenimports