# Create symlink
ln -s /root/shared/RainRemoval /detectron/lib/datasets/data/RainRemoval

# Copy new entry in dataset_catalog
cp /root/shared/rainsnoweval/dataset_catalog.py /detectron/lib/datasets/dataset_catalog.py

# Copy batch script to run the detection
cp /root/shared/rainsnoweval/runDetectron.sh /detectron/runDetectron.sh
