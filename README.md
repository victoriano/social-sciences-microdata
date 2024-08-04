# Social Sciences Public Microdata ready for analysis

This is a collection of ***Python scripts*** designed to process ***public data*** from polls conducted by both public and private institutions, helping you better understand societies worldwide.

All the data in this collection is ***microdata***, meaning it is ***disaggregated to the individual level*** and includes many associated variables. This type of data can help understand potential causes and effects related to demographics, living conditions, the impact of public policies, voter behavior, and much more.

A lot of this data comes in ***difficult-to-use formats***, like fixed-width files in txt, or proprietary formats like SPSS or Stata, and is spread across multiple files for different years. This makes it hard to compile and identify trends. Plus, the data would be much more useful if it were enriched with additional datasets, such as census data, which can be hard to locate and prepare.


These scripts were created to address many of these issues by automating tasks, which ***saves a lot of time and prepares the data for analysis*** to solve complex and interesting questions, such as:

    - Which product and services categories have seen increased consumption among the wealthy in the past five years?

    - What’s the probability of someone voting for X party given their age, gender, region, education level, and economic status?

The author, [Victoriano Izquierdo](https://x.com/victorianoi), founder of [Graphext](https://graphext.com) (the best tool for exploratory data analysis), is originally from Spain, so most of the initial data is about this country. But this repo more than welcome contributions from other countries and geographies, please feel free to submit your pull requests.

I respect that many people, especially in academia, prefer not to share these kinds of scripts because they see it as an advantage over their peers. Fortunately, there are also many others who are passionate about sharing and collaborating to uncover new, fascinating insights that can inspire the development of better policies for everyone.

## Spain

| Data | Description | Remarks | 
|---------|-------------|-----------|
| ***Barometro_CIS*** | Periodic survey on public opinion in Spain | Automatic donwload of all barómetros since 2013 and merging of SPSS files into a CSV or Parquet format | process_barometro_merged.py |
| ***Encuesta_de_Presupuestos_Familiares_INE*** | Annual household budget survey | Automatic downloading of all surveys since 2016 until the present, merging the SPSS into CSVs and Parquet and scrip to convert for 2023 fixed width file into CSV enriched with labels | 
