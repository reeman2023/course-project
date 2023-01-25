import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
from tqdm import tqdm
from pandas.api.types import is_numeric_dtype


mydata = pd.read_csv("data.csv")
data_zero = mydata.fillna(0)
data_null = mydata.loc[mydata['Email'].notnull()].fillna(0).drop(columns=["Rubic"])

# find rubric and its weight
keys = list(mydata.keys())
rubric1 = []
weight1 = []

for k in keys:
    if is_numeric_dtype(mydata[k].iloc[0]):
        rubric1.append(k)
        weight1.append(mydata[k].iloc[0])

dict1 = {
    "rubric": rubric1,
    "weight": weight1}
df1 = pd.DataFrame(dict1)
df1 = df1.dropna()
df1 = df1.reset_index(drop=True)
rubric2 = df1["rubric"].values.tolist()
weight2 = df1["weight"].values.tolist()


class PDF(FPDF):

    def header(self):
        self.set_font('Times', 'BI', 16)
        self.set_fill_color(116, 185, 255)
        self.cell(w=0, h=10, txt='Course Performance', border=1, ln=1, align='C', fill=True)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 12)
        page_number = self.page_no()
        self.cell(w=0, h=10, txt="page "+str(page_number), border=0, ln=0, align='C')


def pie_chart():
    fig, ax = plt.subplots()
    activity_weight = weight2[:-1]
    activity_labels = rubric2[:-1]

    ax.pie(activity_weight, radius=1, labels=activity_labels, wedgeprops=dict(edgecolor='white', linewidth=3),
           autopct='%.f%%')
    ax.set_title("Weights of Course Activities")
    return plt


def stud_chart(std_grade):
    labels = rubric2
    full_grade = weight2
    your_grade = std_grade
    x = np.arange(len(labels))
    width = 0.3
    fig, ax = plt.subplots()
    ax.bar(x, full_grade, width, label='Full Grade', color='red')
    ax.bar(x, your_grade, 0.8*width, label='Your Grade', color='blue')
    ax.set_ylabel('Grades')
    ax.set_title('Activities')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation='vertical')
    plt.legend(["Full Grade", "Your Grade"], loc="upper left")
    fig.tight_layout()
    return plt


def rank_chart(std_total, std_name):
    fd_sort = data_null[["NAME", "TOTAL GRADE"]].sort_values(by='TOTAL GRADE')
    y_values = fd_sort["TOTAL GRADE"].tolist()
    names = fd_sort["NAME"].tolist()
    labels = []
    for n in names:
        if n == std_name:
            lname = std_name
        else:
            lname = " "
        labels.append(lname)

    colr = ['red' if (y == std_total) else 'blue' for y in y_values]
    x = np.arange(len(labels))
    width = 0.9
    fig, ax = plt.subplots()
    ax.bar(x, y_values, width, color=colr)
    ax.set_ylabel("Grades")
    ax.set_title("Whole Class")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation="vertical", fontsize=8)
    return plt


for i in tqdm(range(len(data_null))):
    data2 = data_null.iloc[i]
    pdf = PDF()
    pdf.add_page()
    pdf.ln(5)
    pdf.set_font('Times', 'I', 14)
    pdf.cell(w=35, h=7, txt='Student Name: ', border=0, ln=0, align='L')
    pdf.set_font('Times', 'BU', 14)
    pdf.cell(w=30, h=7, txt=data2['NAME'], border=0, ln=1, align='L')
    pdf.ln(15)
    pdf.set_font('Times', 'BU', 14)
    pdf.cell(w=0, h=7, txt="1. Student Grades in each activity", border=0, ln=1, align='L')
    pdf.set_font('Times', 'I', 10)
    ch = 8
    pdf.ln(5)

    # student activity grades in table

    for r in rubric2:
        pdf.cell(w=30, h=ch, txt=str(r), border=1, ln=0, align='C')

    pdf.ln(8)
    pdf.set_font('Times', 'B', 12)
    for r in rubric2:
        pdf.cell(w=30, h=ch, txt=data2[r].astype(str), border=1, ln=0, align='C')

    pdf.ln(15)
    keys = list(data2.keys())
    missed_activity = []
    for k in keys:
        if data2[k] == 0:
            missed_activity.append(k)

    pdf.set_font('Times', 'BU', 14)
    pdf.cell(w=0, h=ch, txt="2. Activity that you missed or didn't submit", border=0, ln=1, align='L')
    pdf.set_font('Times', '', 10)
    pdf.cell(w=0, h=ch, txt=str(missed_activity), border=0, ln=1, align='L')

    pdf.ln(10)
    pdf.set_font('Times', 'BU', 14)
    pdf.cell(w=100, h=ch, txt="3. Weights of Course Activities", border=0, ln=1, align='L')
    pie_chart().savefig('./pichart.png', transparent=False, facecolor='white')
    pdf.image('./pichart.png', w=0, h=100, type='PNG')

    pdf.add_page()
    pdf.ln(5)
    pdf.set_font('Times', 'BU', 14)
    pdf.cell(w=100, h=ch, txt="4. Student grades as a fraction of the total grade", border=0, ln=1, align='L')
    grades_list = data2[rubric2].values.tolist()
    std_chart = stud_chart(grades_list)
    std_chart.savefig('./student_chart.png', transparent=False, facecolor='white')
    pdf.image('./student_chart.png', w=0, h=100, type='PNG')

    pdf.ln(5)
    pdf.set_font('Times', 'BU', 14)
    pdf.cell(w=100, h=ch, txt="5. Student rank within the whole class", border=0, ln=1, align='L')
    students_rank = rank_chart(data2["TOTAL GRADE"], data2["NAME"])
    students_rank.savefig('./student_rank.png', transparent=False, facecolor='white')
    pdf.image('./student_rank.png', w=0, h=100, type='PNG')

    pdf.output("./reports/"+data2['NAME'] + ".pdf")
