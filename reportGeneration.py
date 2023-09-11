from dbfunc import viewReport
import io
import csv
from flask import Response

async def generateReport():
    data = viewReport()
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    for row in data:
        csv_writer.writerow(row)
    return csv_data.getvalue()
    
    return response
