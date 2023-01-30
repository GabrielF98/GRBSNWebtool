# The GRB-SN Webtool repository /github/release/babel/babel/stable
This repository hosts the data and code for the [GRB-SN Webtool](). This tool was developed to allow astronomers to more easily share and evaluate data for GRB-SN associations, by bringing many sources and types of data together in one place.

The GRB-SN Webtool was created by Gabriel Finneran and Antonio Martin-Carrillo at University College Dublin. An in depth look at the tool can be found in this [paper]().

# Missing/bad data or missing GRB-SN associations 
If you are aware of any missing observations, erroneous data or additional bulk data (e.g. isotropic energy/magnitude) for any of the events in the catalogue you can log this as an issue [here](https://github.com/GabrielF98/GRBSNWebtool/issues/new?assignees=GabrielF98&labels=add+data&template=alert-us-about-missing-data.md&title=Missing+data+for+%3Cevent+name+here%3E). 

If there is an association which has been confirmed and is missing from the tool you can log this as an issue [here](https://github.com/GabrielF98/GRBSNWebtool/issues/new?assignees=GabrielF98&labels=missingGRBSN&template=alert-us-about-missing-event.md&title=Missing+data+for+%3Cevent+name+here%3E).

# Upload your observations
If you have data from your own observations or publications for any of these associations that you wish to upload you can do so by following these steps:
1. [Fork](https://github.com/GabrielF98/GRBSNWebtool/fork) this repository. 
2. Format your files accoring to [these instructions](https://github.com/GabrielF98/GRBSNWebtool/tree/master/Webtool/static/SourceData). An example file is shown here:
```
date	time	freq	flux_density	dflux_density	VLA_Project_Code	date_unit	time_unit	freq_unit	flux_density_unit
2004-Dec-09	621.2	1.4	650	70	AF414	yyyy-month-deciday	days	GHz	microJy
2004-Dec-09	621.2	8.5	250	30	AF414	yyyy-month-deciday	days	GHz	microJy
2004-Dec-23	635.1	1.4	590	70	AF414	yyyy-month-deciday	days	GHz	microJy
```
3. Upload your files to the source folder for the relevant GRB-SN. These source files can be found at [Webtool/static/SourceData](https://github.com/GabrielF98/GRBSNWebtool/tree/master/Webtool/static/SourceData).

4. Ensure that the `readme.txt` file for the GRB-SN is updated correctly after data is added. This file contains the filename, the source (e.g. a NASA ADS link to the paper), the type of data (e.g. Radio) and any notes associated with the data. An example is shown here: 

```
Event Name: GRB030329-SN2003dh
=========================================================
Filename: GRB030329-SN2003dh_Radio.txt
Source: https://ui.adsabs.harvard.edu/abs/2013ApJ...774...77M/abstract
Data-type: Late, Radio
---------------------------------------------------------
Notes: Observations of the GRB 030329 Radio Afterglow at 1.4, 4.9, and 8.5 GHz Taken from the NRAO Data Archive and Not Appearing in a Previous Publication
=========================================================
Filename: GRB030329-SN2003dh_Radio2.txt
Source: https://ui.adsabs.harvard.edu/abs/2012ApJ...759....4M/abstract
Data-type: Late, Radio
---------------------------------------------------------
Notes: VLA and WSRT Observations of the GRB 030329 Radio Afterglow at 5 GHz

Notes: The data were taken under VLA project codes AF414^1, AK583^2, AS864^3, and TYP100^4, and WSRT sequence numbers 10502389^5, 10506025^6, and 10602115^7. WSRT data appearing in this table correspond to data from van der Horst et al. (2005, 2008) that were re-analyzed to ensure uniformity of analysis across all data points.
```

5. Submit a pull request. The pull request should contain:
 * Name of source(s) for which data is being added.
 * Name(s) of the uploaded file(s). 
 * Type of data contained in each file - radio, x-ray, optical etc. 
 * The name and citation information for the repository or paper where this data appears
 * Any other relevant information
 * The pull request should be set for review by: GabrielF98
 * The label should be set to: 'add data'

# Suggest improvements to the Webtool
This repository contains the source code for the project as well as the data stored in the tool. Feel free to suggest updates by opening a [new issue](https://github.com/GabrielF98/GRBSNWebtool/issues/new) or by forking the code and submitting a pull request.
