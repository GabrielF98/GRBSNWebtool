# The GRB-SN Webtool repository
This repository hosts the data and code for the GRB-SN Webtool. This tool was developed to share and evaluate all data related to GRB-SN associations, by bringing many sources and types of data together in one place.

The GRB-SN Webtool was created by Gabriel Finneran and Antonio Martin-Carrillo at University College Dublin. An in depth look at the tool can be found in this [paper]().

# Alert us about missing/bad data or omitted GRB-SN associations 
If you are aware of any missing observations, erroneous data or additional bulk data (e.g. isotropic energy/magnitude) for any of the events in the catalogue you can log this as an issue [here](https://github.com/GabrielF98/GRBSNWebtool/issues/new?assignees=GabrielF98&labels=add+data&template=alert-us-about-missing-data.md&title=Missing+data+for+%3Cevent+name+here%3E). 

If there is an association which has been confirmed and is missing from the tool you can log this as an issue [here](https://github.com/GabrielF98/GRBSNWebtool/issues/new?assignees=GabrielF98&labels=missingGRBSN&template=alert-us-about-missing-event.md&title=Missing+data+for+%3Cevent+name+here%3E)

# Upload your observations
If you have data from your own observations or publications for any of these associations that you wish to upload you can do so by following these steps::
1. [Fork](https://github.com/GabrielF98/GRBSNWebtool/fork) this repository. 
2. Add your files directly to the source folder for that particular GRB-SN. These source files can be found at [Webtool/static/SourceData](https://github.com/GabrielF98/GRBSNWebtool/tree/master/Webtool/static/SourceData). Files should be uploaded as txt format where possible.
3. Ensure that the readme.txt file for the GRB-SN is updated correctly after data is added. This file contains the filename, the source (e.g. a NASA ADS link to the paper), the type of data (e.g. Radio) and any notes associated with the data. An example is shown here: 

```
Event Name: GRB030329-SN2003dh
=========================================================
Filename: GRB030329-SN2003dh_Radio.txt
Source: https://ui.adsabs.harvard.edu/abs/2013ApJ...774...77M/abstract
Data-type: Late, Radio
---------------------------------------------------------
Observations of the GRB 030329 Radio Afterglow at 1.4, 4.9, and 8.5 GHz Taken from the NRAO Data Archive and Not Appearing in a Previous Publication
=========================================================
Filename: GRB030329-SN2003dh_Radio2.txt
Source: https://ui.adsabs.harvard.edu/abs/2012ApJ...759....4M/abstract
Data-type: Late, Radio
---------------------------------------------------------
VLA and WSRT Observations of the GRB 030329 Radio Afterglow at 5 GHz

Notes. The data were taken under VLA project codes AF414^1, AK583^2, AS864^3, and TYP100^4, and WSRT sequence numbers 10502389^5, 10506025^6, and 10602115^7. WSRT data appearing in this table correspond to data from van der Horst et al. (2005, 2008) that were re-analyzed to ensure uniformity of analysis across all data points.
```

4. Submit a pull request. The pull request should contain:
 * Name of source(s) for which data is being added.
 * Name(s) of the uploaded file(s). 
 * Type of data contained in each file - radio, x-ray, optical etc. 
 * The name and citation information for the repository or paper where this data appears
 * Any other relevant information
 * The pull request should be set for review by: GabrielF98
 * The label should be set to: 'add data'

An example of a well formatted text file is provided below, please format text files in a similar fashion where possible to make it easier to add data to the tool. This example was adapted from the text files provided for the optical data for SN2020bvc from _'Near-Infrared and Optical Observations of Type IC SN2020oi and broad-lined IC SN2020bvc: Carbon Monoxide, Dust and High-Velocity Supernova Ejecta'_ [Rho et al. 2021](https://ui.adsabs.harvard.edu/abs/2021ApJ...908..232R%2F/abstract).

```
Title: Near-Infrared and Optical Observations of Type IC SN2020oi and 
       broad-lined IC SN2020bvc: Carbon Monoxide, Dust and High-Velocity 
       Supernova Ejecta  
Authors: Rho J., Evans A., Geballe T.R., Banerjee D.P.K., Hoeflich P., 
         Shahbandeh M., Valenti S., Yoon S.-C., Jin H., Williamson M., 
         Modjaz M., Hiramatsu D., Howell D.A., Pellegrino C., Vinko J., 
         Cartier R., Burke J., McCully C., An H., Cha H., Pritchard T., 
         Wang X., Andrews J., Galbany L., Van Dyk S., Graham M.L., 
         Blinnikov S., Joshi V., Pal A., Kriskovics L., Ordash A., Szakats R.,
         Vida K., Chen Z., Li X., Zhang J., Yan S. 
Figure: Multi-color light curves of SN2020bvc
================================================================================
Byte-by-byte Description of file: dbf4.txt
--------------------------------------------------------------------------------
   Bytes Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1-  9 F9.3   d       MJD     Modified Julian Date
  11- 19 F9.6   mag     mag     Apparent magnitude in Filter
  21- 34 F14.10 mag   e_mag     Uncertainty in mag
      36 A1     ---     Filter  Filter used
  38- 40 A3     ---     Tel     Telescope code (1)
--------------------------------------------------------------------------------
Note (1):
    ZTF = Zwicky Transient Facility;
    KON = The 0.8m RC80 telescope of Konkoly Observatory;
    LCO = Las Cumbres Observatory network with the Sinistro cameras on the 1m
          telescopes at Sutherland (South Africa), CTIO (Chile), Siding Spring
          (Australia), and McDonald (USA), through the Global Supernova Project.
--------------------------------------------------------------------------------
58887.510 17.062800   0.034800000  U LCO 
58887.513 17.460000   0.024900000  B LCO 
58887.515 17.464100   0.024900000  B LCO 
58887.517 16.985400   0.021600000  V LCO 
58887.518 16.976600   0.022200000  V LCO 
58887.519 17.478500   0.014500000  g LCO 
```

# Suggest improvements to the Webtool
This repository contains the source code for the project as well as the data stored in the tool. Feel free to suggest updates by opening a [new issue](https://github.com/GabrielF98/GRBSNWebtool/issues/new) or by forking the code and submitting a pull request.
