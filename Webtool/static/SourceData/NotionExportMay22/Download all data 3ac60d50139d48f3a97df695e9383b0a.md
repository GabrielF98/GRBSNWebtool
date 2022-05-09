# Download all data

Created: October 14, 2021 8:39 PM
Priority: P1 🔥
Status: Constant
Type: Epic

# Description

- The graphs on the event pages will require data
- Downloading this data is crucial for the webtool
- It will need to be amalgamated for each of the events

### Explanation of the Status Tags

<aside>
💡 **Not started:** Pretty self-explanatory

</aside>

<aside>
💡 **New Event:** This is a young discovery so there may not be much on the ADS yet

</aside>

<aside>
💡 **In progress:** I am working on Gathering Data from the ADS and the full list in the ADS has not been gathered (some of these are labelled wrong since I didnt add the ADS exhausted tag until later)

</aside>

<aside>
💡 **No ADS data:** We havent been able to find any refereed papers with data in the ADS

</aside>

<aside>
💡 **No Dowloadables:** We havent been able to find any refereed papers with downloadable data in the ADS

</aside>

<aside>
💡 **ADS exhausted:** I have gathered data from all the references which appear in the ADS when you search obj:GRB XXXXXX, abs:"XXXXXX" with only refereed papers used.

</aside>

<aside>
💡 **Mostly completed:** 3/4 of the main categories we want have been found and downloaded and we have looked at all papers in the ADS.

</aside>

<aside>
💡 **Completed:** The holy grail that won't happen for most of these because people made it hard to find the data or didnt bother getting it.

</aside>

### Explanation of Early and Late tags

<aside>
💡 **Early: Prior to 15 days after burst/SN t0**

</aside>

<aside>
💡 **Late: After the burst/SN t0 by 15 days**

</aside>

### Plan of attack

- [x]  There are 58 sources and 3 weeks of 15 days. So i need to get the data for 4 GRB-SN pairs per day

[Source List](Download%20all%20data%203ac60d50139d48f3a97df695e9383b0a/Source%20List%20c1f1bfea218c40e2a1267b9e69618838.csv)

# Problems with the data

- The tables are all in different file formats
- The tables are layed out differently
- Tables often dont tell you the magnitude system
- ADS often runs out before i have info on all the bands
- Wont be possible to have X-ray for all the bursts in the same way swift provides it
- Spectra are often shown only as graphs but not in a way that allows you to download and reproduce them
- Sometimes the files have no header lines to say what each column is
- Sometimes they forget to say its Vega or AB in the table, only in the text
- Its often the case that there are multiple header lines, eg one with column name and one with the units of that column. These then have to be put into one line
- People also put the errors in the columns with the data sometimes so I'll need to split that up too