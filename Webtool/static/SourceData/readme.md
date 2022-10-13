# Data Standardisation

One of the major aims of the GRBSN webtool is to make all of the data for GRB-SNe available in one location. Key to this is the conversion of all of the data into a common format. This format is described in this readme for the benefit of the end users.

# How to standardise your data for upload to the webtool
The data should be converted to the format shown below. Here is an example file:

```
date	time	freq	flux_density	dflux_density	VLA_Project_Code	date_unit	time_unit	freq_unit	flux_density_unit
2004-Dec-09	621.2	1.4	650	70	AF414	yyyy-month-deciday	days	GHz	microJy
2004-Dec-09	621.2	8.5	250	30	AF414	yyyy-month-deciday	days	GHz	microJy
2004-Dec-23	635.1	1.4	590	70	AF414	yyyy-month-deciday	days	GHz	microJy
```

There are two types of column: one type contains data, and the other type of column describes the units for the data column. The columns and the data therin are separated by tabs. The categories available for the data are listed in the next section. 

The filename should contain the name of the GRB, name of the SN and the type of data in the file. For example: GRB030329-SN2003dh_Radio.txt



# Categories available in the webtool
It is important to note that these headings will not appear in all files. They only appear if
the original data fits into one of these categories. The list is organised by category, then column, 
then the associated unit columns and units. 

If a 'd' precedes a column name, e.g. `dmag`, this is an error column for the relevant datatype, the units are the same as for the datatype.

### Dates and Times
One or both of these data will be present in each file.

  * `date` The date of observation. 
  
  * `date_unit` The unit of the date of observation, the options are:
  
    * `yyyy-month-deciday` The year, month and decimal day.
    
    *`yyyy-mm-deciday` The year, numerical month and  decimal day.
    
    *`yyyy-month-dd-hh:mm:ss` The year, month, day and hours, min, sec.
    
    *`yyyy-mm-deciday-deciday` The year, numerical month and  decimal day - range.
    
    *`yyyy-month-deciday-month-deciday` The year, month and deciday, both are ranges.
    
    * `yyyy-month-deciday-deciday` The year, month and decimal day - range.
    
    * `yyyy-month-dd-hh:mm` The year, month, day and hours and minutes.
    
    * `yyyy-mm-dd-hh:mm-hh:mm` Epoch range in standard time format
    * `yyyy-month-dd-hh.h-hh.h` Year, month, day and decimal hour range.
    
    * `MJD` Modified Julian Day.
    * `MJD-MJD` Modified Julian Day - range. 
  
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
   
   * `Unspecified` For when neither AB nor Vega are clearly specified.
   
 * `flux` The received flux of the source.
 
 * `flux unit`  The units used for the flux of the source. The options are:
 
   * `erg/cm^2/sec` 
 * `flux_density`
 * `flux_density_unit`
   * `milliJy` milli Janskys
   * `microJy` micro Janskys


### Bands/Filters/Wavelengths/Frequencies
The descriptions of the bands are listed here for reference purposes.
  * `band` The filter that the data was taken in. The following list of bands are used:
   
    **Johnson-Cousins Filters**
    * `U`
    
    * `B`
    * `V`
    * `R`
    * `H`
    * `I`
    * `J`
    * `K_{s}`
    * `R_{C}`
    * `J_{s}`
    * `R_{special}`
    * `I_{C}`

    **Hubble Space Telescope Filters**
    * `F450W`
    
    * `F555W`
    * `F702W`
    * `F814W`
    * `F850LP`

 * `wavelength` The wavelength that the data was taken at.
 
 * `wavelength_unit` The unit used for the wavelength. The options are: 
 
   * `angstrom` 

    **X-ray Observatory Frequency Ranges**
    * `energy_range` The range of energies covered by the observation.
    * `flux` The flux within the energy band. Usually going to be:
     * `erg/cm^2/sec`
    
    **Radio Observing Bands**
    * `freq` The frequency of the radio observation.
    
    * `freq_unit` The unit of the frequency. GHz/MHz.
    * `beam` The size of the telescope beam, measured in arcseconds.
    * `bandwidth` The bandwidth of the observation
    * `bandwidth_unit` Unit of the bandwidth. GHz/MHz.
    
    **Spectra**

    `

### Miscellaneous
 * `instrument` The names of the instrument used to take data. The options are:
 
   * `HST` The Hubble Space Telescope
   
   * `OGLE 1.3 m`
   * `Baade 6.5 m`
   * `Baade`
   * `CTIO 4 m`
   * `dP` The duPont 2.5m telescope
   * `AAT`
  
 * `integration` The duration of the measurement. The default time unit is seconds.
 * `integration_unit` The units for the integration time.
 
 * `seeing` The seeing in arcseconds.
 * `extinction` The extinction in the associated band and with the associated units.
 
 * `counts` The total counts received by a CCD or other instrument.
 
 * `kcorr` The k correction. This will be followed by the relevant bands being corrected between e.g. `kcorr_vs` for correction from V to STIS.

 * `optical_depth` Sometimes listed for radio.
 * `position_angle` Sometimes used in radio. 
 * `polarisation` Measured in radio on occasion.
 * `system_noise_temp` The radio system noise temperature in Kelvin
