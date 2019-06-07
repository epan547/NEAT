# Processing FITS Images from NEAT
1. Run `NEAT_Downloader.py`. Specify what you want to download: 
```python
NEAT_vol_1 = 'https://sbnarchive.psi.edu/pds3/neat/geodss/data/'
NEAT_vol_2 = 'https://sbnarchive.psi.edu/pds3/neat/tricam/data/'
NEAT_vol_3 = 'https://sbnarchive.psi.edu/pds3/neat/tricam2/data/'

NEAT_vol_1_data = pullVolumeData(NEAT_vol_1)
palomar = getRecordsFromVolumeData(NEAT_vol_1_data, 10)
fetchRecords(palomar)
```

2. Run `FITS_preprocessor.py`. Processed images will be saved in a folder called obsdata_reduction. Again, specify what you want to process:
```python
geodss_data_volume = 'geodss'
tricam_data_volume = 'tricam'
tricam2_data_volume = 'tricam2'

# change this to choose which to process: geodss, tricam, tricam2, etc
target_volume = tricam_data_volume
```
3. Run `FITS_Sextractor.py`. Check images and output catalogs will be saved in a folder called `sexout`. Modify parameters in `sexconf`. 

```python
geodss_data_volume = 'geodss'
tricam_data_volume = 'tricam'
tricam2_data_volume = 'tricam2'

# change this to source extract different data
target_volume = geodss_data_volume
```
