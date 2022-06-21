# Data Standardisation

We have undertaken to convert all data gathered for the GRBSN webtool into a common format. 
The format is described in this document for the benefit of the end users.

## Categories available in the webtool
It is important to note that these headings will not appear in all files. They only appear if
the original data fits into one of these categories. The list is organised by category, then column, 
then the associated unit columns and units.

### Dates and Times
One or both of these data will be present in each file.

  * `date` The date of observation. 
  
  * `date_unit` The unit of the date of observation, the options are:
  
    * `yyyy-month-deciday` The year, month and decimal day.
    
    * `MJD` Modified Julian Day.
  
  * `time` The elapsed time since the reference point of the data. For GRBs this will usually be the trigger time but could also be the peak time of the SN lightcurve.
  
  * `time_unit` The elapsed time unit, the options are:
  
    * `seconds`
    
    * `kiloseconds`
    
    * `hours`
    
    * `days`

### Observed Data
 * `mag` Magnitude of the source.
 
 * `mag_unit` The units used for the magnitude of the source. The options are:
 
   * `Vega` 
   
   * `AB`
   
 * `flux` The received flux of the source.
 
 * `flux unit`  The units used for the flux of the source. The options are:
 
   * `erg/cm^2/sec` 


### Bands and Filters
The descriptions of the bands are listed here for reference purposes.
  * `band` The wavelength range/filter that the data was taken in. The following list of bands are used:
   
    **Johnson-Cousins Filters**
    * `U`
    
    * `B`
    * `V`
    * `R`
    * `I`
    * `J`

    **Hubble Space Telescope Filters**
    * `F450W`
    
    * `F555W`
    * `F702W`
    * `F814W`
    * `F850LP`

    **X-ray Observatory Frequency Ranges**
    
    **Radio Observing Bands**
    
    **Spectra**

### Miscellaneous
 * `instrument` The names of the instrument used to take data. The options are:
 
   * `HST` The Hubble Space Telescope
   
   * `OGLE 1.3 m`
   * `Baade 6.5 m`
   * `CTIO 4 m`
