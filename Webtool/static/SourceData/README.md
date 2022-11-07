# Data Standardisation

One of the major aims of the GRBSN webtool is to make all of the data for GRB-SNe available in one location. Key to this is the conversion of all of the data into a common format. This format is described in this readme for the benefit of the end users.

# Filenames
The filename should contain the name of the GRB, name of the SN and the type of data in the file. For example: GRB030329-SN2003dh_Radio.txt

All filenames should contain one of the following tags:

* `Xray` Any file containing observations from an X-ray telescope/satellite. 

* `Optical` Any file containing observations in the `NIR`, `IR`, Visible or `UV` ranges. 

* `Radio` Any file containing observations at Radio wavelengths. 

* `Spectra` Any file containing spectroscopic observations. 

If a file contains `NIR`, `IR` or `UV` data then it should also contain the relevant tag in it's filename. The filename should always contain the Optical tag even if there is no optical data in the file. 

In the case of a filename with multiple tags, each tag should be separated by an underscore. For example: GRB030329-SN2003dh_Optical_NIR.txt

If there are several files in the same wavelength, e.g. multiple optical files, an index should be added to each filename. For example: GRB030329-SN2003dh_Optical.txt, GRB030329-SN2003dh_Optical1.txt and GRB030329-SN2003dh_Optical2.txt.

# Formatting
The data should be converted to the format shown below. Here is an example file:

```
date	time	freq	flux_density	dflux_density	VLA_Project_Code	date_unit	time_unit	freq_unit	flux_density_unit
2004-Dec-09	621.2	1.4	650	70	AF414	yyyy-month-deciday	days	GHz	microJy
2004-Dec-09	621.2	8.5	250	30	AF414	yyyy-month-deciday	days	GHz	microJy
2004-Dec-23	635.1	1.4	590	70	AF414	yyyy-month-deciday	days	GHz	microJy
```

There are two main types of column: one type contains data, and the other type of column describes the units for the data column. The columns and the data therin are separated by tabs. The categories available for the data are listed below. 

If a 'd' precedes a column name, e.g. `dmag`, this is an error column for the relevant datatype, the units are the same as for the datatype.

If '_limit' comes after a column name, e.g. `mag_limit`, this is a limit column for the relevant datatype. Is the data an upper limit (1), not a limit (0) or a lower limit (-1). Added by the plotfuncs.py code. 

# File Headers
The following keywords appear in the headers of the webtool files. Not all keywords appear in all master files. They only appear if
the original data fits into one of these categories. The list is organised by category, then column, 
then the associated unit columns and units. 

### Common keywords
Keywords that might appear in any file. 

***Dates and Times***

Time should always appear in all files. Sometimes the date will also appear. 

  * `date` The date of observation. 
  
  * `date_unit` The unit of the date of observation. The options are:
  
    * `yyyy-month-deciday` The year, month and decimal day.
    
    * `yyyy-mm-deciday` The year, numerical month and  decimal day.
    
    * `utc` = `yyyy-mm-ddThh:mm:ss` UTC time format. The year, numerical month, then a T, then day and hours, min, sec.
    
    * `yyyy-month-dd-hh:mm:ss` The year, month, day and hours, min, sec.
    
    * `yyyy-mm-deciday-deciday` The year, numerical month and  decimal day - range.
    
    * `yyyy-month-deciday-month-deciday` The year, month and deciday, both are ranges.
    
    * `yyyy-month-deciday-deciday` The year, month and decimal day - range.
    
    * `yyyy-month-dd-hh:mm` The year, month, day and hours and minutes.
    
    * `yyyy-mm-dd-hh:mm-hh:mm` Epoch range in standard time format
    * `yyyy-month-dd-hh.h-hh.h` Year, month, day and decimal hour range.
    
    * `MJD` Modified Julian Day.
    * `MJD-MJD` Modified Julian Day - range. 
  
  * `time` The elapsed time since the reference point of the data. If known, the GRB trigger time is used, otherwise the peak time of the SN lightcurve is used.
  
  * `time_unit` Unit for the elapsed time. The options are:
  
    * `seconds`
    
    * `kiloseconds`
    
    * `hours`
    
    * `days`
    
 * `dtime` Error on the time. 

***Miscellaneous***
* `integration` The duration of the observation. The default unit is seconds. This may have been converted from an exposure column in the original file. 

* `integration_unit` The units for the integration time. Standard time units will be used. 

* `reference` Usually added by the plotfuncs.py code, this is taken from the `filesources.csv` file and provides a direct url to the paper or resource from which the file came.

* `instrument` The names of the instrument used to take data. The options are:
 
   * `HST` The Hubble Space Telescope
   * `OGLE 1.3 m`
   * `Baade 6.5 m`
   * `Baade`
   * `CTIO 4 m`
   * `dP` The duPont 2.5m telescope
   * `AAT` 
    
### Spectra keywords
* `obs_wavelength` The observed wavelength of the observation. 

* `rest_wavelength` The rest frame wavelength of the observation. Calculated by dividing the observed wavelength by 1+z, where z is the redshift. 

* `wavelength_unit` Unit for wavelength. The options are: 
   * `angstroms`for angstroms.
   * `nm` for nanometers.

* `flux` The observed flux.

* `flux_unit` Unit for the flux. The options are: 
   *  `uncalibrated` used when we don't know the unit or when the flux is uncalibrated; 
   *  `calibrated` is used when some calibration has been done but the units were not provided; 
   *  `erg/s/cm2/A` erg per second per square cm per angstrom.

* `redshift` If not already in the file this will be obtained from one of the references in the table at the top of the event webpage. 

* `sky_flux` Sometimes measured when spectra are taken. It is in the same units as the flux of the source. 

### Xray keywords
* `flux` The received flux of the source.
 
* `flux unit`  The units used for the flux of the source. The options are:
   * `erg/cm^2/sec`

* `dflux` The error on the source flux. 

* `flux_limit` Is the source flux an upper limit (1), not a limit (0) or a lower limit (-1). Added by the plotfuncs.py code. 

* `energy_range` The energy range of the xray data.

### Radio keywords
* `freq` The frequency of the radio band. 

* `freq_unit` The unit for the frequency of the radio band. The options are:
   * `GHz`
   * `MHz`

* `flux_density` The flux density of the source. 

* `dflux_density` Error on the flux density. 

* `flux_density_unit` The unit for the flux density of the source. The options are:
   * `milliJy` milli Jansky. 
   * `microJy` micro Jansky. 

* `flux_density_limit` Is the flux density an upper limit (1), not a limit (0) or a lower limit (-1). Added by the plotfuncs.py code.  

* `seeing` The seeing. Default unit is `arcseconds`.

* `beam` The size of the telescope beam, default unit is `arcseconds`.

* `beam_unit` The unit associated with the beam. The options are: 
   * `arcseconds^2`

* `bandwidth` The bandwidth of the observation.

* `bandwidth_unit` Unit of the bandwidth. The options are:
   * `GHz`
   * `MHz`

* `optical_depth` Optical depth along the line of sight to the source. 

* `polarisation` Degree of polarisation of the source.

* `system_noise_temp` The radio system noise temperature in Kelvin. 

* `VLA_Project_Code` Used in VLA data. 

* `position_angle`  

### Optical keywords 
* `mag` Magnitude of the source.

* `dmag`/`dmag2` Error on the magnitude. `dmag2` represents a second error column used when there are assymmetric errors. 

* `mag_unit` The units used for the magnitude of the source. The options are:

  * `Vega` 

  * `AB`

  * `unspecified` Used when neither AB nor Vega are clearly specified.

* `mag_limit` Is the magnitude an upper limit (1), not a limit (0) or a lower limit (-1). Added by the plotfuncs.py code.

* `seeing` The seeing. Default unit is `arcseconds`.

* `counts` The total counts received by a CCD or other instrument.

* `dcounts` The error on the counts.

* `flux_density` The flux density of the source. 

* `dflux_density` Error on the flux density. 

* `flux_density_unit` The unit for the flux density of the source. The options are:
   * `milliJy` milli Jansky. 
   * `microJy` micro Jansky. 

* `flux_density_limit` Is the flux density an upper limit (1), not a limit (0) or a lower limit (-1). Added by the plotfuncs.py code.

* `extinction` The correction to the magnitude due to extinction, measured in the associated band and with the associated units.

* `kcorr` The k correction. Used in optical/NIR/UV This will be followed by the relevant bands being corrected between e.g. `kcorr_vs` for correction from V to STIS.
  * `kcorr_bs`

* `wavelength` The wavelength of the observtion. 

* `wavelength_unit` Unit for wavelength. The options are: 
   * `angstroms`for angstroms.
   * `nm` for nanometers.

* `airmass` Airmass.

* `band` The filter used for the observation. A list of the bands is given here for reference purposes:
   
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
