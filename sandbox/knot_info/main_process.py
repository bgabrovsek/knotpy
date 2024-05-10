
import pandas


df = pandas.read_excel("knotinfo_data_complete.xls")

extract = ["name", "pd_notation", "jones_polynomial"]

df[extract][1:].to_csv("name-pd-jones.csv", index=False, header=True)
